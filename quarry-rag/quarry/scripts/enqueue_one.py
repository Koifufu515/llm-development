"""原文命令入口；实现见 enqueue_doc.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.enqueue_doc", run_name="__main__")
