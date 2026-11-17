from pathlib import Path
from src.analyzer import run

ROOT = Path(__file__).resolve().parent
analysis, incidents, summary = run(ROOT / "data" / "raw", ROOT / "data" / "processed")

print("NetPulse AI pipeline completed.")
print(f"Telemetry readings processed : {len(analysis):,}")
print(f"Devices monitored            : {analysis['device_id'].nunique():,}")
print(f"Incidents detected           : {len(incidents):,}")
print(f"Critical incidents           : {(incidents['severity'] == 'Critical').sum():,}")
print(f"Warning incidents            : {(incidents['severity'] == 'Warning').sum():,}")
print("\nTop devices by incident count:")
print(summary[["device_id", "device_name", "incidents", "avg_health_score"]].head(5).to_string(index=False))
print("\nPower BI-ready files saved in data/processed/")
