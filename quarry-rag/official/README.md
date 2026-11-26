# 官方数据与演示数据

`demo-travel-guide.csv`逐字保留原文三行演示值，其中example.com链接和票价不是现实官方核验，不能用于真实价格回答。

正常维护时，在`travel-guide.csv`填入自行核实的数据：实体、别名、属性、季节、值、核实日期、官方来源URL。导入器按原方案整体校验后事务替换。当前travel-guide.csv维护官网核对的秦始皇帝陵博物院普通成人票价，按全年/旺季/淡季三个严格匹配键表示同一政策；具体核实范围及日期见核实记录.md，其他景点仍保持unverified。

原文verified / expired / unverified、冲突替换、官方更新、遮蔽与权限演示通过`scripts/verify_workflows.py`在隔离集合实现，不污染公共攻略。示例本身保留，未删减事实层功能。
