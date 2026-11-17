CREATE DATABASE IF NOT EXISTS netpulse;
USE netpulse;

CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(20) PRIMARY KEY,
    device_name VARCHAR(60) NOT NULL,
    device_type VARCHAR(30) NOT NULL,
    site VARCHAR(60) NOT NULL,
    ip_address VARCHAR(45) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS telemetry (
    telemetry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recorded_at DATETIME NOT NULL,
    device_id VARCHAR(20) NOT NULL,
    cpu_utilization_pct DECIMAL(5,2) NOT NULL,
    latency_ms DECIMAL(8,2) NOT NULL,
    packet_loss_pct DECIMAL(5,2) NOT NULL,
    availability TINYINT NOT NULL,
    severity VARCHAR(15) NOT NULL,
    anomaly_reason VARCHAR(255),
    health_score DECIMAL(5,2),
    CONSTRAINT fk_telemetry_device FOREIGN KEY (device_id)
        REFERENCES devices(device_id),
    CONSTRAINT chk_cpu CHECK (cpu_utilization_pct BETWEEN 0 AND 100),
    CONSTRAINT chk_packet_loss CHECK (packet_loss_pct BETWEEN 0 AND 100),
    CONSTRAINT chk_availability CHECK (availability IN (0,1))
);

CREATE INDEX idx_telemetry_device_time ON telemetry(device_id, recorded_at);
CREATE INDEX idx_telemetry_severity ON telemetry(severity);
