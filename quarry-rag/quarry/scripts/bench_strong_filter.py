"""原文命令入口；实现见 bench_filter.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.bench_filter", run_name="__main__")
