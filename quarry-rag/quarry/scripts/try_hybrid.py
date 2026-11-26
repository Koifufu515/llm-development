"""原文命令入口；实现见 try_retrieval.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.try_retrieval", run_name="__main__")
