# OpsInsight — Power BI Report Design

**Version:** 1.0  

---

## Report Overview

**File:** OpsInsight.pbix  
**Pages:** 5  
**Theme:** Segoe UI, blue primary (#1B4FD8), white background  
**Slicers:** Date Range, Department, Priority, Status (all pages)

---

## Page 1: Executive Overview

**Purpose:** Single-glance operational health dashboard for leadership.

**Layout (16:9):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ OpsInsight — Executive Overview          [Date ▼] [Dept ▼] [Priority ▼]    │
│─────────────────────────────────────────────────────────────────────────────│
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │
│  │Total Issues│ │Open Issues│ │SLA Compli.│ │Avg Resol. │ │SLA Breach │    │
│  │   2,200   │ │    490    │ │   87.3%   │ │  8.4 hrs  │ │    325    │    │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘    │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Issue Trend (Monthly)            │  │ Issues by Department (Bar)   │   │
│  │ Line: Created vs Resolved        │  │ IT: 602 | FIN: 479 | ...     │   │
│  │ Jan-Sep 2026                     │  │                              │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────┐  ┌───────────────────┐  ┌──────────────────────┐    │
│  │ By Priority       │  │ By Status         │  │ Monthly SLA %        │    │
│  │ (Donut chart)     │  │ (Stacked bar)     │  │ (Line trend)         │    │
│  └──────────────────┘  └───────────────────┘  └──────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Top 8 Categories by Volume (Horizontal bar)                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**KPI Card Colors:**
- Total Issues: neutral grey border
- Open Issues: blue (#1B4FD8) border
- SLA Compliance: green if >85%, amber if 70-85%, red if <70%
- Avg Resolution: neutral
- SLA Breach: red border always

**Key Insight Text (static textbox):**
> "SLA Compliance stands at 87.3%. Finance and Procurement show the lowest compliance rates. See SLA Performance page for detail."

---

## Page 2: SLA Performance

**Purpose:** Compliance deep-dive by dimension.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SLA Performance                          [Date ▼] [Dept ▼] [Priority ▼]   │
│─────────────────────────────────────────────────────────────────────────────│
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐                  │
│  │SLA Compli.│ │ Breached  │ │Avg SLA %  │ │Critical   │                  │
│  │  87.3%    │ │   325     │ │   64.2%   │ │   171     │                  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘                  │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ SLA Compliance by Department     │  │ SLA Compliance by Category   │   │
│  │ (Clustered bar — sorted ASC)     │  │ (Bar — worst 10)             │   │
│  │ PROC: 72% | FIN: 78% | ...       │  │ Approval Delay: 58%          │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────┐  ┌───────────────────────────────────────────────┐  │
│  │ SLA by Priority  │  │ Monthly SLA Compliance Trend (Line)           │  │
│  │ (Donut)          │  │ Shows improvement or decline over 9 months    │  │
│  └──────────────────┘  └───────────────────────────────────────────────┘  │
│                                                                             │
│  Top 5 Most Breached Categories (Bar — count of breaches)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Conditional Formatting:**
- SLA Compliance bars: green > 90%, amber 75-90%, red < 75%
- Use data bars on category table to show volume context

---

## Page 3: Process Bottleneck Analysis

**Purpose:** The project's signature insight page.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Process Bottleneck Analysis              [Date ▼] [Dept ▼]                 │
│─────────────────────────────────────────────────────────────────────────────│
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Average Hours per Process Stage (Horizontal bar — sorted DESC)       │  │
│  │                                                                      │  │
│  │ Waiting       ████████████████  12.4h                                │  │
│  │ In Progress   ████████          6.1h                                 │  │
│  │ Assigned      ██                1.8h                                 │  │
│  │ New           █                 0.4h                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Avg Waiting Hours by Department  │  │ Status Duration by Category  │   │
│  │ (Bar chart)                      │  │ (Matrix — Category vs Stage) │   │
│  │ PROC: 18.2h ← BOTTLENECK        │  │ Shows waiting concentration  │   │
│  │ FIN: 11.4h                       │  │                              │   │
│  │ IT: 4.1h                         │  │                              │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌───────────────┐  ┌────────────────┐  ┌──────────────────────────────┐  │
│  │Avg Transfers  │  │Avg Status      │  │ Top 10 Longest Open Issues   │  │
│  │per Issue: 0.18│  │Changes: 2.4    │  │ (Table — IssueNumber, Age,   │  │
│  │               │  │                │  │  Priority, Team)             │  │
│  └───────────────┘  └────────────────┘  └──────────────────────────────┘  │
│                                                                             │
│ 💡 Insight: "Procurement issues spend 61% of lifecycle in Waiting status.  │
│    This indicates an approval process bottleneck."                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Design Decision:** Insight text is a static textbox updated per demo context.

---

## Page 4: Root Cause Analysis

**Purpose:** Move management from reactive to proactive.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Root Cause Analysis                      [Date ▼] [Dept ▼] [Category ▼]   │
│─────────────────────────────────────────────────────────────────────────────│
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Top Root Causes (Horizontal bar — count of issues)                   │  │
│  │ Missing Approval   ████████████████  387                             │  │
│  │ Data Quality       ██████████        281                             │  │
│  │ Process Design     ████████          198                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Root Causes by Department        │  │ Root Cause vs SLA Breach %   │   │
│  │ (Stacked bar)                    │  │ (Scatter plot or bar)        │   │
│  │ Shows composition per dept       │  │ Missing Approval has highest │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Root Cause vs Avg Resolution     │  │ Reopened Issues by Category  │   │
│  │ (Bar — which causes take longer) │  │ (Shows recurrence signal)    │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Root Cause × Category Matrix (Heatmap / conditional formatted table) │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Page 5: Team Performance

**Purpose:** Capacity and efficiency measurement.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Team Performance                         [Date ▼] [Team ▼]                 │
│─────────────────────────────────────────────────────────────────────────────│
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Team Summary Table                                                   │  │
│  │ Team Name | Assigned | Resolved | Avg Hrs | SLA% | Backlog | Reopen%│  │
│  │ IT Apps   |   412    |   380    |  6.2    | 91%  |   32    |  5.2%  │  │
│  │ IT Infra  |   190    |   175    |  9.8    | 84%  |   15    |  7.1%  │  │
│  │ Fin Ops   |   289    |   265    |  10.4   | 79%  |   24    |  9.3%  │  │
│  │ ...       |   ...    |   ...    |   ...   |  ... |    ...  |   ...  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Team Backlog (Current)           │  │ Monthly Resolution Trend     │   │
│  │ (Clustered bar)                  │  │ (Line per team)              │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Issues Assigned vs Resolved      │  │ SLA Compliance by Team (Bar) │   │
│  │ (Grouped bar — throughput)       │  │ Sorted ASC (worst first)     │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│ NOTE: This page measures team capacity and process efficiency.              │
│ It is NOT intended as an individual performance ranking tool.               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Visual Colour Rules (Conditional Formatting)

| Metric | Green (Good) | Amber (Warning) | Red (Bad) |
|--------|-------------|-----------------|-----------|
| SLA Compliance % | > 90% | 75–90% | < 75% |
| Backlog | < 20 | 20–50 | > 50 |
| Avg Resolution Hours | < SLA Target | 70–100% of target | > SLA Target |
| Reopen Rate % | < 5% | 5–10% | > 10% |
| SLA Breach Count | 0 | 1–5 | > 5 |

---

## Performance Notes

- Import mode recommended for demo scale (2,000 issues)
- Scheduled refresh not required for portfolio demo
- Incremental refresh if dataset exceeds 100,000 rows
- Page-level filters preferred over report-level for flexibility
