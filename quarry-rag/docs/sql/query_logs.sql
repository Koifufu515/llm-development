-- 原文8.9的四条只读分析SQL。请按语句独立执行。

SELECT caller_id,
       count(*) AS requests,
       round(avg((status >= 400)::int) * 100, 1) AS error_pct,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY (timings->>'total_ms')::float) AS p95_ms
FROM query_logs
WHERE created_at > now() - interval '24 hours'
GROUP BY caller_id;


SELECT date_trunc('day', created_at)::date AS day,
       count(*) AS requests,
       round(avg(abstain::int) * 100, 1) AS abstain_pct
FROM query_logs
WHERE status = 200
GROUP BY 1
ORDER BY 1 DESC
LIMIT 14;


SELECT request_id, query, (timings->>'total_ms')::float AS total_ms, timings
FROM query_logs
WHERE status = 200
ORDER BY total_ms DESC NULLS LAST
LIMIT 10;


SELECT query, count(*) AS times
FROM query_logs
WHERE status = 200 AND abstain AND created_at > now() - interval '7 days'
GROUP BY query
ORDER BY times DESC
LIMIT 20;


