"""原文命令入口；实现见 bench_async.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.bench_async", run_name="__main__")
