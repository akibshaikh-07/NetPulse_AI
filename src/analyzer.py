"""Rule-based network telemetry analysis for simulated monitoring data."""
from pathlib import Path
import pandas as pd

REQUIRED = {
    "timestamp", "device_id", "cpu_utilization_pct",
    "latency_ms", "packet_loss_pct", "availability"
}

def load_telemetry(path):
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    numeric = ["cpu_utilization_pct", "latency_ms", "packet_loss_pct", "availability"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["timestamp", "device_id"] + numeric).copy()
    df = df.drop_duplicates(subset=["timestamp", "device_id"], keep="last")
    return df

def classify_incident(row):
    """Apply transparent thresholds; this is not ML or confirmed root-cause diagnosis."""
    reasons = []
    if row["availability"] == 0:
        reasons.append("Device unavailable")
    if row["cpu_utilization_pct"] >= 90:
        reasons.append("Critical CPU utilization")
    elif row["cpu_utilization_pct"] >= 80:
        reasons.append("High CPU utilization")
    if row["latency_ms"] >= 200:
        reasons.append("Critical latency")
    elif row["latency_ms"] >= 100:
        reasons.append("High latency")
    if row["packet_loss_pct"] >= 5:
        reasons.append("Critical packet loss")
    elif row["packet_loss_pct"] >= 2:
        reasons.append("Elevated packet loss")

    if not reasons:
        return pd.Series(["Normal", "No threshold breach", "No incident"])
    critical = (
        row["availability"] == 0
        or row["cpu_utilization_pct"] >= 90
        or row["latency_ms"] >= 200
        or row["packet_loss_pct"] >= 5
    )
    severity = "Critical" if critical else "Warning"
    return pd.Series([severity, "; ".join(reasons), "Investigate device and interface"])

def analyze(telemetry, devices):
    df = telemetry.merge(devices, on="device_id", how="left", validate="many_to_one")
    if df["device_name"].isna().any():
        unknown = sorted(df.loc[df["device_name"].isna(), "device_id"].unique())
        raise ValueError(f"Telemetry contains unknown device IDs: {unknown}")
    df[["severity", "anomaly_reason", "recommended_action"]] = df.apply(classify_incident, axis=1)
    df["incident_flag"] = (df["severity"] != "Normal").astype(int)
    df["health_score"] = (
        100
        - (df["cpu_utilization_pct"].clip(0, 100) * 0.25)
        - (df["latency_ms"].clip(0, 300) / 300 * 25)
        - (df["packet_loss_pct"].clip(0, 20) / 20 * 30)
        - ((1 - df["availability"].clip(0, 1)) * 20)
    ).clip(0, 100).round(1)
    return df

def build_incidents(analysis):
    incidents = analysis.loc[analysis["incident_flag"] == 1].copy()
    incidents.insert(0, "incident_id", [f"INC-{i:05d}" for i in range(1, len(incidents)+1)])
    return incidents[[
        "incident_id", "timestamp", "device_id", "device_name", "device_type",
        "site", "severity", "anomaly_reason", "recommended_action",
        "cpu_utilization_pct", "latency_ms", "packet_loss_pct", "availability"
    ]]

def build_device_summary(analysis):
    summary = analysis.groupby(
        ["device_id", "device_name", "device_type", "site"], as_index=False
    ).agg(
        readings=("timestamp", "count"),
        incidents=("incident_flag", "sum"),
        avg_cpu_pct=("cpu_utilization_pct", "mean"),
        avg_latency_ms=("latency_ms", "mean"),
        avg_packet_loss_pct=("packet_loss_pct", "mean"),
        availability_pct=("availability", lambda s: s.mean() * 100),
        avg_health_score=("health_score", "mean")
    )
    return summary.round(2).sort_values(["incidents", "avg_health_score"], ascending=[False, True])

def run(raw_dir, output_dir):
    raw_dir, output_dir = Path(raw_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    telemetry = load_telemetry(raw_dir / "network_telemetry.csv")
    devices = pd.read_csv(raw_dir / "devices.csv")
    analysis = analyze(telemetry, devices)
    incidents = build_incidents(analysis)
    summary = build_device_summary(analysis)
    analysis.to_csv(output_dir / "network_analysis.csv", index=False)
    incidents.to_csv(output_dir / "incidents.csv", index=False)
    summary.to_csv(output_dir / "device_summary.csv", index=False)
    return analysis, incidents, summary
