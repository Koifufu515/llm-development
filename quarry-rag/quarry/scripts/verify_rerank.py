"""原文命令入口；实现见 smoke_rerank.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.smoke_rerank", run_name="__main__")
