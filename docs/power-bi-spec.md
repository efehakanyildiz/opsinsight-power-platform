# OpsInsight — Power BI Specification

**Version:** 1.0  
**Date:** October 2026  

---

## 1. Data Source Setup

### Local Development (CSV)
Connect Power BI Desktop to CSVs in `data/generated/`:
- issues.csv
- issue_history.csv
- departments.csv
- teams.csv
- employees.csv
- categories.csv
- sla_rules.csv
- root_causes.csv
- resolution_codes.csv
- escalations.csv

### Production (Dataverse)
Use the **Dataverse** connector in Power BI Desktop:
- Environment: Your Power Apps developer environment
- Tables: All OpsInsight tables
- Import mode (recommended for demo scale)

---

## 2. Power Query (M) Transformations

### issues query

```m
let
    Source = Csv.Document(File.Contents("../data/generated/issues.csv"),
        [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    // Type conversions
    TypedTable = Table.TransformColumnTypes(PromotedHeaders, {
        {"IssueId", type text},
        {"IssueNumber", type text},
        {"Title", type text},
        {"Description", type text},
        {"CreatedBy", type text},
        {"CreatedAt", type datetime},
        {"DepartmentId", type text},
        {"CategoryId", type text},
        {"AssignedTeamId", type text},
        {"AssignedAgentId", type text},
        {"Priority", type text},
        {"Status", type text},
        {"SLAId", type text},
        {"SLADeadline", type datetime},
        {"FirstResponseAt", type datetime},
        {"ResolvedAt", type datetime},
        {"ClosedAt", type datetime},
        {"RootCauseId", type text},
        {"ResolutionCodeId", type text},
        {"ReopenCount", Int64.Type},
        {"LastUpdatedAt", type datetime}
    }),
    
    // Null handling — replace empty strings with null for datetime fields
    CleanedSLADeadline = Table.ReplaceValue(TypedTable, "", null, 
        Replacer.ReplaceValue, {"SLADeadline"}),
    CleanedResolvedAt = Table.ReplaceValue(CleanedSLADeadline, "", null,
        Replacer.ReplaceValue, {"ResolvedAt", "ClosedAt", "FirstResponseAt"}),
    
    // Calculated columns
    WithPriorityOrder = Table.AddColumn(CleanedResolvedAt, "PriorityOrder", each
        if [Priority] = "Critical" then 1
        else if [Priority] = "High" then 2
        else if [Priority] = "Medium" then 3
        else 4, Int64.Type),
    
    WithIsResolved = Table.AddColumn(WithPriorityOrder, "IsResolved", each
        [Status] = "Resolved" or [Status] = "Closed", type logical),
    
    WithIsSLABreached = Table.AddColumn(WithIsResolved, "IsSLABreached", each
        if [SLADeadline] = null then false
        else if [IsResolved] and [ResolvedAt] <> null then [ResolvedAt] > [SLADeadline]
        else DateTime.LocalNow() > [SLADeadline], type logical),
    
    WithCreatedMonth = Table.AddColumn(WithIsSLABreached, "CreatedMonth", each
        Date.StartOfMonth([CreatedAt]), type date),
    
    WithCreatedYear = Table.AddColumn(WithCreatedMonth, "CreatedYear", each
        Date.Year([CreatedAt]), Int64.Type),
    
    // Data quality: remove rows with null IssueId
    Filtered = Table.SelectRows(WithCreatedYear, each [IssueId] <> null and [IssueId] <> "")
    
in
    Filtered
```

### issue_history query

```m
let
    Source = Csv.Document(File.Contents("../data/generated/issue_history.csv"), ...),
    PromotedHeaders = Table.PromoteHeaders(Source),
    TypedTable = Table.TransformColumnTypes(PromotedHeaders, {
        {"HistoryId", type text},
        {"IssueId", type text},
        {"EventType", type text},
        {"PreviousStatus", type text},
        {"NewStatus", type text},
        {"PreviousTeam", type text},
        {"NewTeam", type text},
        {"ChangedBy", type text},
        {"ChangeTimestamp", type datetime},
        {"Notes", type text}
    }),
    Sorted = Table.Sort(TypedTable, {{"ChangeTimestamp", Order.Ascending}})
in
    Sorted
```

### Date Dimension Table (calculated in Power Query)

```m
let
    StartDate = #date(2026, 1, 1),
    EndDate = #date(2026, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    TypedDate = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    WithYear = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    WithMonth = Table.AddColumn(WithYear, "Month", each Date.Month([Date]), Int64.Type),
    WithMonthName = Table.AddColumn(WithMonth, "MonthName", 
        each Date.ToText([Date], "MMMM"), type text),
    WithQuarter = Table.AddColumn(WithMonthName, "Quarter", 
        each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    WithWeekday = Table.AddColumn(WithQuarter, "Weekday", 
        each Date.DayOfWeekName([Date]), type text),
    WithIsWeekend = Table.AddColumn(WithWeekday, "IsWeekend",
        each Date.DayOfWeek([Date]) = 0 or Date.DayOfWeek([Date]) = 6, type logical)
in
    WithIsWeekend
```

---

## 3. Semantic Model — Relationships

```
DimDate[Date] ──1:N──► Issues[CreatedAt date]
Departments[DepartmentId] ──1:N──► Issues[DepartmentId]
Departments[DepartmentId] ──1:N──► Teams[DepartmentId]
Teams[TeamId] ──1:N──► Issues[AssignedTeamId]
IssueCategories[CategoryId] ──1:N──► Issues[CategoryId]
SLARules[SLAId] ──1:N──► Issues[SLAId]
RootCauses[RootCauseId] ──1:N──► Issues[RootCauseId]
ResolutionCodes[ResolutionCodeId] ──1:N──► Issues[ResolutionCodeId]
Issues[IssueId] ──1:N──► IssueHistory[IssueId]
Issues[IssueId] ──1:N──► Escalations[IssueId]
```

All relationships are single direction (one-to-many). Cross-filter direction: single.

---

## 4. Report Pages

---

### PAGE 1: Executive Overview

**Purpose:** Single-glance operational health summary for leadership.

**KPI Cards (top row):**

| KPI | DAX Measure |
|-----|-------------|
| Total Issues | [Total Issues] |
| Open Issues | [Open Issues] |
| Resolved Issues | [Resolved Issues] |
| SLA Compliance % | [SLA Compliance %] |
| Avg Resolution Time (hrs) | [Avg Resolution Time Hours] |
| SLA Breached | [SLA Breached Issues] |
| Backlog | [Backlog] |
| Reopen Rate | [Reopen Rate %] |

**Visuals:**

| Visual | Type | Axes |
|--------|------|------|
| Issue Trend | Line chart | X: Month, Y: Count, Series: Open/Resolved |
| Issues by Department | Clustered bar | X: Dept, Y: Count |
| Issues by Priority | Donut chart | Legend: Priority |
| Issues by Status | Stacked bar | X: Status, Y: Count |
| Top Issue Categories | Bar chart | X: Count, Y: Category (top 8) |
| Monthly SLA Compliance | Line chart | X: Month, Y: SLA Compliance % |

---

### PAGE 2: SLA Performance

**Purpose:** Deep dive into SLA compliance patterns.

**KPI Cards:**

| KPI | Measure |
|-----|---------|
| SLA Compliance % | [SLA Compliance %] |
| Breached Issues | [SLA Breached Issues] |
| Avg SLA Consumed % | [Avg SLA Consumed %] |
| Critical SLA Issues | [SLA Critical Issues] |

**Visuals:**

| Visual | Type | Axes |
|--------|------|------|
| SLA Compliance by Department | Clustered bar | X: Dept, Y: Compliance % |
| SLA Compliance by Category | Bar chart | X: Category, Y: % |
| SLA Compliance by Priority | Donut | Legend: Priority |
| SLA Trend over Time | Line | X: Month, Y: Compliance % |
| Top Breached Categories | Bar | X: Count of breached, Y: Category |
| SLA Status Distribution | Donut | Legend: SLA Status |

---

### PAGE 3: Process Bottleneck Analysis

**Purpose:** Reveal where time is lost in the issue lifecycle. The project's most strategic insight page.

**Key Insight Visuals:**

| Visual | Type | Description |
|--------|------|-------------|
| Avg Time per Process Stage | Bar chart | Shows time in New, Assigned, In Progress, Waiting |
| Time in Waiting by Department | Clustered bar | Identifies approval bottlenecks |
| Status Duration by Category | Matrix | Category vs Status vs Avg Hours |
| Avg Transfers per Issue | KPI | How often issues change hands |
| Avg Status Changes per Issue | KPI | Complexity indicator |
| Longest-Running Issues | Table | Top 10 issues by age |
| Waiting % by Category | Bar | % of lifecycle in Waiting |

**Business Insight Example (to highlight in presentation):**
> "Procurement issues spend 61% of their lifecycle in Waiting status, indicating an approval process bottleneck."

---

### PAGE 4: Root Cause Analysis

**Purpose:** Move management from reactive to proactive.

**Visuals:**

| Visual | Type | Description |
|--------|------|-------------|
| Top Root Causes | Horizontal bar | Count of issues by root cause |
| Root Causes by Department | Stacked bar | Root cause composition per dept |
| Root Cause by Category | Matrix | Category vs Root Cause |
| Root Cause vs Avg Resolution | Bar | Which causes take longest |
| Root Cause vs SLA Breach Rate | Scatter | Risk quadrant |
| Reopened Issues by Category | Bar | Identifies quality issues |
| Month-over-Month Recurrence | Line | Tracking same root causes over time |

---

### PAGE 5: Team Performance

**Purpose:** Capacity and efficiency analysis. Not a surveillance tool.

**KPI Cards per Team:**

| Metric | Measure |
|--------|---------|
| Issues Assigned | Count of assigned issues |
| Issues Resolved | [Resolved Issues] |
| Avg Resolution Time | [Avg Resolution Time Hours] |
| SLA Compliance | [SLA Compliance %] |
| Current Backlog | [Backlog] |
| Reopen Rate | [Reopen Rate %] |

**Visuals:**

| Visual | Type | Description |
|--------|------|-------------|
| Team Backlog Comparison | Clustered bar | Current open issues per team |
| Resolution Time Trend | Line | Monthly avg by team |
| SLA Compliance by Team | Bar | % compliance per team |
| Issues Assigned vs Resolved | Grouped bar | Throughput comparison |
| Workload Distribution | Treemap | Volume by team |
| Team Resolution Trend | Small multiples line | Per-team over time |

---

## 5. Slicers (All Pages)

| Slicer | Field | Type |
|--------|-------|------|
| Date Range | DimDate[Date] | Date range picker |
| Department | Departments[DepartmentName] | Dropdown |
| Priority | Issues[Priority] | Checkbox list |
| Status | Issues[Status] | Checkbox list |

---

## 6. Report Theme

**Colors:**
- Primary: #1B4FD8 (blue)
- Accent 2: #DC2626 (red for critical/breach)
- Accent 3: #D97706 (amber for warning)
- Accent 4: #16A34A (green for healthy/resolved)
- Background: #FFFFFF
- Alternate: #F8F9FA

**Fonts:** Segoe UI (consistent with Power Platform)

**Card style:** Minimal shadow, white background, colored accent border on left

---

## 7. Bookmarks & Navigation

Create bookmarks for:
- Executive View (default)
- SLA Deep Dive
- Process Analysis
- Reset All Slicers

Navigation buttons in header allow quick page switching within the report.

---

## 8. Local Development Setup

1. Install Power BI Desktop (free from Microsoft)
2. Open Power BI Desktop → Get Data → Text/CSV
3. Load all CSV files from `data/generated/`
4. Apply Power Query transformations per Section 2
5. Define relationships per Section 3
6. Create DAX measures per `measures.md`
7. Build report pages per Section 4
8. Save as .pbix file in `power-bi/` directory

*Note: .pbix files are excluded from git (binary format). Document the design in this spec instead.*
