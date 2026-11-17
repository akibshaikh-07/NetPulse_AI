USE netpulse;

-- 1. Number of incidents by severity
SELECT severity, COUNT(*) AS incident_count
FROM telemetry
WHERE severity <> 'Normal'
GROUP BY severity
ORDER BY incident_count DESC;

-- 2. Devices with the most threshold breaches
SELECT d.device_id, d.device_name, d.site,
       COUNT(*) AS incident_count
FROM telemetry t
JOIN devices d ON d.device_id = t.device_id
WHERE t.severity <> 'Normal'
GROUP BY d.device_id, d.device_name, d.site
ORDER BY incident_count DESC;

-- 3. Average performance by device
SELECT d.device_name,
       ROUND(AVG(t.cpu_utilization_pct), 2) AS avg_cpu_pct,
       ROUND(AVG(t.latency_ms), 2) AS avg_latency_ms,
       ROUND(AVG(t.packet_loss_pct), 2) AS avg_packet_loss_pct
FROM telemetry t
JOIN devices d ON d.device_id = t.device_id
GROUP BY d.device_id, d.device_name
ORDER BY avg_latency_ms DESC;

-- 4. Hourly incident trend
SELECT HOUR(recorded_at) AS hour_of_day,
       COUNT(*) AS incident_count
FROM telemetry
WHERE severity <> 'Normal'
GROUP BY HOUR(recorded_at)
ORDER BY hour_of_day;

-- 5. Availability by site
SELECT d.site,
       ROUND(AVG(t.availability) * 100, 2) AS availability_pct
FROM telemetry t
JOIN devices d ON d.device_id = t.device_id
GROUP BY d.site
ORDER BY availability_pct ASC;
