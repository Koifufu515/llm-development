"""原文命令入口；实现见 audit_facts.py。"""
import runpy

if __name__ == "__main__":
    runpy.run_module("quarry.scripts.audit_facts", run_name="__main__")
