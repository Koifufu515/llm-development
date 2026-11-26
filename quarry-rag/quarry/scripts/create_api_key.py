"""原文命令入口；实现见 create_key.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.create_key", run_name="__main__")
