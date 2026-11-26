"""原文命令入口；实现见 try_parser.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.try_parser", run_name="__main__")
