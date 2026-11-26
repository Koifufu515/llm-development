#!/usr/bin/env python3
"""Start and stop this project's local services without system-wide autostart."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'
LOGS = LOCAL / 'logs'
STATE = LOCAL / 'processes.json'
PYTHON = ROOT / 'backend/.venv/bin/python'


def environment(**extra):
    result = dict(os.environ)
    result.update({k: v for k, v in dotenv_values(ROOT / '.env').items() if v is not None})
    result.update({'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:' + result.get('PATH', ''),
                   'PYTHONUNBUFFERED': '1', 'NEXT_TELEMETRY_DISABLED': '1'})
    result.update(extra)
    return result


def read_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def write_state(state):
    STATE.write_text(json.dumps(state, indent=2))


def alive(item):
    try:
        output = subprocess.check_output(['ps', '-p', str(item['pid']), '-o', 'stat=,command='], text=True).strip()
        state, _, command = output.partition(' ')
        return bool(command) and not state.startswith('Z') and item['marker'] in command
    except (subprocess.CalledProcessError, ProcessLookupError):
        return False


def listening(port):
    with socket.socket() as connection:
        connection.settimeout(.3)
        return connection.connect_ex(('127.0.0.1', port)) == 0


def start_one(name, command, port=None, cwd=None, extra=None, marker=None):
    state = read_state()
    if name in state and alive(state[name]):
        print(f'{name}: 已运行 (PID {state[name]["pid"]})', flush=True)
        return
    if port and listening(port):
        raise RuntimeError(f'端口 {port} 已被其他进程占用；请先释放端口后重试。')
    with (LOGS / f'{name}.log').open('ab') as log:
        process = subprocess.Popen([str(s) for s in command], cwd=cwd or ROOT,
                                   env=environment(**(extra or {})), stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    state[name] = {'pid': process.pid, 'marker': marker or str(command[0]), 'port': port}
    write_state(state)
    for _ in range(240):
        if process.poll() is not None:
            raise RuntimeError(f'{name} 启动失败，请查看 {LOGS / (name + ".log")}')
        if not port or listening(port):
            print(f'{name}: 已启动 (PID {process.pid})', flush=True)
            return
        time.sleep(.25)
    raise RuntimeError(f'{name} 启动超时，请查看日志。')


def wait_http(url):
    for _ in range(180):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, TimeoutError):
            pass
        time.sleep(.5)
    raise RuntimeError(f'HTTP 健康检查超时：{url}')


def start(open_browser=False):
    LOGS.mkdir(parents=True, exist_ok=True)
    for folder in ['data/mongodb', 'data/redis', 'uploads']:
        (LOCAL / folder).mkdir(parents=True, exist_ok=True)
    redis = shutil.which('redis-server', path=environment()['PATH'])
    node = shutil.which('node', path=environment()['PATH'])
    if not redis or not node:
        raise RuntimeError('找不到 redis-server 或 node，请检查本地部署说明。')
    start_one('mongodb', [LOCAL / 'mongodb/bin/mongod', '--dbpath', LOCAL / 'data/mongodb',
                          '--bind_ip', '127.0.0.1', '--port', '27027', '--logpath', LOGS / 'mongodb-server.log',
                          '--logappend'], port=27027)
    start_one('redis', [redis, LOCAL / 'redis.conf'], port=6387, marker='127.0.0.1:6387')
    marker = LOCAL / 'initialized'
    if not marker.exists():
        print('正在初始化部门和导入样例文档……', flush=True)
        with (LOGS / 'initialize.log').open('ab') as log:
            for module, arguments in [('scripts.seed_data', []),
                                      ('scripts.ingest_department_files', ['--base', str(ROOT / 'department_files')])]:
                subprocess.run([str(PYTHON), '-m', module, *arguments], cwd=ROOT / 'backend',
                               env=environment(), stdout=log, stderr=subprocess.STDOUT, check=True)
        marker.write_text(time.strftime('%Y-%m-%d %H:%M:%S'))
    start_one('pi-agent', [node, ROOT / 'services/pi-agent/dist/index.js'], port=8100,
              cwd=ROOT / 'services/pi-agent', extra={'PORT': '8100', 'HOST': '127.0.0.1'})
    start_one('backend', [PYTHON, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
              port=8000, cwd=ROOT / 'backend', marker='uvicorn app.main:app --host 127.0.0.1 --port 8000')
    wait_http('http://127.0.0.1:8000/healthz')
    start_one('worker', [PYTHON, '-m', 'scripts.async_worker'], cwd=ROOT / 'backend',
              marker='scripts.async_worker')
    start_one('frontend', [node, ROOT / 'web/.next/standalone/server.js'], port=3000, cwd=ROOT / 'web',
              extra={'PORT': '3000', 'HOSTNAME': '127.0.0.1', 'BACKEND_URL': 'http://127.0.0.1:8000'},
              marker='next-server')
    wait_http('http://127.0.0.1:3000')
    print('\n文枢已启动：http://127.0.0.1:3000\n接口文档：http://127.0.0.1:8000/docs', flush=True)
    if open_browser:
        subprocess.run(['open', 'http://127.0.0.1:3000'], check=False)


def stop():
    state = read_state()
    for name in ['frontend', 'worker', 'backend', 'pi-agent', 'redis', 'mongodb']:
        item = state.get(name)
        if not item or not alive(item):
            continue
        try:
            os.killpg(item['pid'], signal.SIGTERM)
        except ProcessLookupError:
            pass
        print(f'{name}: 已发送停止请求', flush=True)
        # Keep databases alive until API/worker cleanup has finished.
        deadline = time.monotonic() + 35
        while alive(item) and time.monotonic() < deadline:
            time.sleep(.25)
    deadline = time.monotonic() + 5
    while any(alive(item) for item in state.values()) and time.monotonic() < deadline:
        time.sleep(.25)
    remaining = {name: item for name, item in state.items() if alive(item)}
    write_state(remaining)
    if remaining:
        raise RuntimeError('部分进程仍未停止：' + ', '.join(remaining))
    print('服务已停止；数据库内容保留。')


def status():
    state = read_state()
    for name in ['mongodb', 'redis', 'pi-agent', 'backend', 'worker', 'frontend']:
        item = state.get(name)
        print(f'{name}: ' + (f'运行中 (PID {item["pid"]})' if item and alive(item) else '未运行'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    parser.add_argument('--open', action='store_true')
    args = parser.parse_args()
    try:
        if args.action == 'start':
            start(args.open)
        elif args.action == 'stop':
            stop()
        else:
            status()
    except Exception as error:
        print(f'部署操作失败：{error}', file=sys.stderr)
        sys.exit(1)
