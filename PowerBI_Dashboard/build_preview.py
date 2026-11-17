"""Builds the interactive dashboard preview (HTML) from the processed CSV files.

Run from the project root:  python PowerBI_Dashboard/build_preview.py
"""
import json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

a = pd.read_csv(DATA / "network_analysis.csv", parse_dates=["timestamp"])
a["hour"] = a["timestamp"].dt.hour
rows = []
for r in a.itertuples():
    rows.append({
        "hour": int(r.hour), "ts": r.timestamp.strftime("%d-%b-%Y %H:%M"),
        "device_id": r.device_id, "device_name": r.device_name,
        "type": r.device_type, "site": r.site,
        "cpu": float(r.cpu_utilization_pct), "lat": float(r.latency_ms),
        "loss": float(r.packet_loss_pct), "avail": int(r.availability),
        "sev": r.severity, "reasons": [] if r.severity == "Normal" else r.anomaly_reason.split("; "),
        "action": r.recommended_action, "flag": int(r.incident_flag), "health": float(r.health_score),
    })
inc = pd.read_csv(DATA / "incidents.csv")
inc_ids = {(x.device_id, x.timestamp): x.incident_id for x in inc.itertuples()}
for r, src in zip(rows, a.itertuples()):
    r["inc_id"] = inc_ids.get((src.device_id, src.timestamp.strftime("%Y-%m-%d %H:%M:%S")), "")

html = (HERE / "dashboard_template.html").read_text(encoding="utf-8")
html = html.replace("__DATA__", json.dumps({"rows": rows}, separators=(",", ":")))
out = HERE / "interactive_preview" / "NetPulse_Dashboard_Preview.html"
out.write_text(html, encoding="utf-8")
print("written", out, f"{out.stat().st_size/1024:.0f} KB")
