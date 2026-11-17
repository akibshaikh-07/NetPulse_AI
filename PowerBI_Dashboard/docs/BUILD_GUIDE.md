# Build the real .pbix in Power BI Desktop (about 25 minutes)

The preview images in `images/` show the target layout. Follow these steps to build the same report in Power BI Desktop and save it as `NetPulse_AI.pbix` in this folder.

## 1. Load data
Home > Get data > Text/CSV. Load all files in `PowerBI_Dashboard/data/`:
`network_analysis.csv`, `incidents.csv`, `device_summary.csv`, `dim_devices.csv`, `dim_hour.csv`.
Transform data: set `timestamp` = Date/Time, numeric telemetry columns = Decimal Number, `availability` and `incident_flag` = Whole Number. Close & Apply.

## 2. Add helper column to network_analysis (Power Query or DAX)
```DAX
hour = HOUR ( network_analysis[timestamp] )
```
In `dim_hour`, select `hour_label` > Column tools > Sort by column > `hour`.

## 3. Model view - relationships (all Many-to-one, single direction)
| From (many) | To (one) |
|---|---|
| network_analysis[device_id] | dim_devices[device_id] |
| incidents[device_id] | dim_devices[device_id] |
| device_summary[device_id] | dim_devices[device_id] |
| network_analysis[hour] | dim_hour[hour] |

## 4. Theme and measures
- View > Themes > Browse for themes > `theme/NetPulse_Theme.json`
- Home > Enter data > create empty table `_Measures`; paste each measure from `dax/measures.dax`.

## 5. Page setup
View > Page view > Actual size. Canvas 1280 x 720 (Format page > Canvas settings > Type: 16:9). Page background `#EAEAEA`. Rename pages: `Network Overview`, `Incident Analysis`, `Device Health`.

## 6. Page 1 - Network Overview
| Visual | Fields |
|---|---|
| Text box (title) | NetPulse AI \| Simulated Network Operations Dashboard |
| Slicer x3 (List style) | dim_devices[site], dim_devices[device_type], network_analysis[severity] |
| Card x5 | Total Devices, Total Incidents, Critical Incidents, Availability % (format 0.00%), Avg Latency (ms) |
| Donut | Legend = severity, Values = Total Incidents; filter severity is not Normal |
| Clustered bar | Axis = dim_devices[site], Values = Total Incidents, sort descending |
| Clustered bar | Axis = dim_devices[device_type], Values = Total Incidents |
| Clustered column | Axis = dim_hour[hour_label], Values = Total Incidents (show data labels) |
| Clustered bar | Axis = dim_devices[device_name], Values = Total Incidents; Top N = 8 |

## 7. Page 2 - Incident Analysis
- Cards: Total Incidents, Critical Incidents, Warning Incidents, Unavailable Events.
- Bar: Axis = `incidents[anomaly_reason]` (in Power Query: Split Column by delimiter `; ` into Rows first), Values = Count of incident_id.
- Bar: Axis = device_name, Values = Total Incidents, Top N = 10.
- Table: incident_id, timestamp, device_name, site, severity, anomaly_reason, cpu, latency, packet loss. Conditional formatting on `severity` using the `Severity Colour` measure.
- Sync the three slicers: View > Sync slicers, tick all pages.

## 8. Page 3 - Device Health
- Cards: Avg Health Score, Avg CPU (%), Avg Latency (ms), Avg Packet Loss (%).
- Bar: Axis = device_name, Values = Avg Health Score, Top N = 10 **bottom**.
- Scatter: X = Avg Latency (ms), Y = Avg Packet Loss (%), Size = Total Incidents, Legend = device_type, Details = device_name.
- Table: device summary columns; Avg health score gets Data bars + Background colour by field value `Health Colour`.

## 9. Interactivity
Format > Edit interactions so slicers filter every visual. Optional: add a "Clear all slicers" bookmark button (Insert > Buttons > Bookmark).

## 10. Save and screenshot
Save as `NetPulse_AI.pbix`. For GitHub, export each page: File > Export > PDF, or take a screenshot, and place the images in `images/` (replace the previews).
