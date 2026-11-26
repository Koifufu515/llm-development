"""原文命令入口；实现见 verify_ids.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.verify_ids", run_name="__main__")
