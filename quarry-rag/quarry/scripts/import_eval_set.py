"""原文命令入口；实现见 import_eval.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.import_eval", run_name="__main__")
