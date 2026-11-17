# Power BI Dashboard Guide

## Import data
Use **Home → Get Data → Text/CSV** and import:
- `data/processed/network_analysis.csv`
- `data/processed/incidents.csv`
- `data/processed/device_summary.csv`

Set `timestamp` to Date/Time and numeric telemetry columns to Decimal Number. Set `availability` and `incident_flag` to Whole Number.

## Suggested relationships
- `network_analysis[device_id]` → `devices` dimension if you create one from the unique device inventory.
- `incidents[device_id]` → same device dimension.
- `device_summary[device_id]` → same device dimension.

For a simple first version, use each exported table independently and avoid ambiguous many-to-many relationships.

## Suggested measures (DAX)

```DAX
Total Devices =
DISTINCTCOUNT(network_analysis[device_id])

Total Readings =
COUNTROWS(network_analysis)

Total Incidents =
CALCULATE(
    COUNTROWS(network_analysis),
    network_analysis[incident_flag] = 1
)

Critical Incidents =
CALCULATE(
    COUNTROWS(network_analysis),
    network_analysis[severity] = "Critical"
)

Average Latency (ms) =
AVERAGE(network_analysis[latency_ms])

Average CPU (%) =
AVERAGE(network_analysis[cpu_utilization_pct])

Average Packet Loss (%) =
AVERAGE(network_analysis[packet_loss_pct])

Availability (%) =
AVERAGE(network_analysis[availability]) * 100

Average Health Score =
AVERAGE(network_analysis[health_score])
```

## Visual layout

### Page 1 — Network Overview
- Cards: Total Devices, Total Incidents, Critical Incidents, Availability (%)
- Donut: Incident count by severity
- Bar chart: Incidents by site
- Line chart: Incidents by hour
- Slicers: Site, device type, severity

### Page 2 — Incident Analysis
- Table: timestamp, device, site, severity, anomaly reason, recommended action
- Bar chart: incident count by anomaly reason
- Column chart: incidents by device

### Page 3 — Device Health
- Table: device, site, average health score, average CPU, latency, packet loss, availability
- Bar chart: average health score by device
- Conditional formatting for low health scores

Use a clear title such as **NetPulse AI | Simulated Network Operations Dashboard**.
