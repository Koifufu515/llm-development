-- 原文30天保留期示例；仅在确定本项目日志保留政策后运行。部署脚本不自动删除记录。
DELETE FROM query_logs WHERE created_at < now() - interval '30 days';
