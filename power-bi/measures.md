# OpsInsight — Power BI DAX Measures

**Version:** 1.0  
**Date:** October 2026  
**Convention:** All measures in dedicated `_Measures` table. PascalCase naming.

---

## Table: _Measures

All DAX measures are stored in a dedicated measures table (no data columns).

---

## 1. Volume Measures

### Total Issues
```dax
Total Issues = 
COUNTROWS(Issues)
```

### Open Issues
```dax
Open Issues = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[Status] IN {"New", "Assigned", "In Progress", "Waiting", "Reopened"}
    )
)
```

### Resolved Issues
```dax
Resolved Issues = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[Status] IN {"Resolved", "Closed"}
    )
)
```

### Closed Issues
```dax
Closed Issues = 
COUNTROWS(
    FILTER(Issues, Issues[Status] = "Closed")
)
```

### Critical Issues
```dax
Critical Issues = 
COUNTROWS(
    FILTER(Issues, Issues[Priority] = "Critical")
)
```

### Backlog
```dax
Backlog = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[Status] IN {"New", "Assigned", "In Progress", "Waiting"}
    )
)
```

### Cancelled Issues
```dax
Cancelled Issues = 
COUNTROWS(
    FILTER(Issues, Issues[Status] = "Cancelled")
)
```

### Reopened Issues
```dax
Reopened Issues = 
COUNTROWS(
    FILTER(Issues, Issues[ReopenCount] > 0)
)
```

---

## 2. SLA Measures

### SLA Breached Issues
```dax
SLA Breached Issues = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[IsSLABreached] = TRUE()
    )
)
```

### SLA Compliant Issues
```dax
SLA Compliant Issues = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[Status] IN {"Resolved", "Closed"}
        && Issues[IsSLABreached] = FALSE()
    )
)
```

### SLA Compliance %
```dax
SLA Compliance % = 
VAR TotalResolved = [Resolved Issues]
VAR Compliant = [SLA Compliant Issues]
RETURN
    IF(
        TotalResolved = 0,
        BLANK(),
        DIVIDE(Compliant, TotalResolved) * 100
    )
```

### SLA Warning Issues
```dax
SLA Warning Issues = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[Status] NOT IN {"Resolved", "Closed", "Cancelled"}
        && NOT Issues[IsSLABreached]
        && DIVIDE(
            DATEDIFF(Issues[CreatedAt], NOW(), MINUTE),
            Issues[SLARules.TargetHours] * 60
           ) >= 0.7
        && DIVIDE(
            DATEDIFF(Issues[CreatedAt], NOW(), MINUTE),
            Issues[SLARules.TargetHours] * 60
           ) < 0.9
    )
)
```

*Note: Use a calculated column SLAPctConsumed for cleaner measure references.*

### SLA Critical Issues
```dax
SLA Critical Issues = 
COUNTROWS(
    FILTER(
        Issues,
        Issues[Status] NOT IN {"Resolved", "Closed", "Cancelled"}
        && NOT Issues[IsSLABreached]
        && Issues[SLAPctConsumed] >= 90
        && Issues[SLAPctConsumed] < 100
    )
)
```

### Avg SLA Consumed %
```dax
Avg SLA Consumed % = 
AVERAGEX(
    FILTER(Issues, Issues[SLAPctConsumed] <> BLANK()),
    Issues[SLAPctConsumed]
)
```

### SLA Breach Rate %
```dax
SLA Breach Rate % = 
DIVIDE([SLA Breached Issues], [Total Issues]) * 100
```

---

## 3. Resolution Time Measures

### Avg Resolution Time Hours
```dax
Avg Resolution Time Hours = 
AVERAGEX(
    FILTER(
        Issues,
        Issues[Status] IN {"Resolved", "Closed"}
        && Issues[ResolvedAt] <> BLANK()
    ),
    DATEDIFF(Issues[CreatedAt], Issues[ResolvedAt], HOUR)
)
```

### Median Resolution Time Hours
```dax
Median Resolution Time Hours = 
MEDIANX(
    FILTER(
        Issues,
        Issues[Status] IN {"Resolved", "Closed"}
        && Issues[ResolvedAt] <> BLANK()
    ),
    DATEDIFF(Issues[CreatedAt], Issues[ResolvedAt], HOUR)
)
```

### Avg First Response Time Hours
```dax
Avg First Response Time Hours = 
AVERAGEX(
    FILTER(
        Issues,
        Issues[FirstResponseAt] <> BLANK()
    ),
    DATEDIFF(Issues[CreatedAt], Issues[FirstResponseAt], HOUR)
)
```

### Avg Issue Age (Days)
```dax
Avg Issue Age Days = 
AVERAGEX(
    FILTER(
        Issues,
        Issues[Status] IN {"New", "Assigned", "In Progress", "Waiting", "Reopened"}
    ),
    DATEDIFF(Issues[CreatedAt], TODAY(), DAY)
)
```

---

## 4. Reopen & Transfer Measures

### Reopen Rate %
```dax
Reopen Rate % = 
DIVIDE(
    COUNTROWS(FILTER(Issues, Issues[ReopenCount] > 0)),
    [Resolved Issues]
) * 100
```

### Avg Reopen Count
```dax
Avg Reopen Count = 
AVERAGEX(
    FILTER(Issues, Issues[ReopenCount] > 0),
    Issues[ReopenCount]
)
```

### Avg Transfers per Issue
```dax
Avg Transfers per Issue = 
VAR TransferCount =
    CALCULATE(
        COUNTROWS(IssueHistory),
        IssueHistory[EventType] = "Transferred"
    )
VAR IssueCnt = [Total Issues]
RETURN
    DIVIDE(TransferCount, IssueCnt)
```

### Avg Status Changes per Issue
```dax
Avg Status Changes per Issue = 
DIVIDE(
    CALCULATE(
        COUNTROWS(IssueHistory),
        IssueHistory[EventType] = "StatusChanged"
    ),
    [Total Issues]
)
```

---

## 5. Time Intelligence Measures

### Issues Created This Month
```dax
Issues Created This Month = 
CALCULATE(
    [Total Issues],
    DATESMTD(DimDate[Date])
)
```

### Issues Resolved This Month
```dax
Issues Resolved This Month = 
CALCULATE(
    [Resolved Issues],
    DATESMTD(DimDate[Date])
)
```

### Issues Created Last Month
```dax
Issues Created Last Month = 
CALCULATE(
    [Total Issues],
    PREVIOUSMONTH(DimDate[Date])
)
```

### Month-over-Month Issue Change
```dax
MoM Issue Change = 
[Issues Created This Month] - [Issues Created Last Month]
```

### MoM Issue Change %
```dax
MoM Issue Change % = 
DIVIDE(
    [MoM Issue Change],
    [Issues Created Last Month]
) * 100
```

### Issues Created YTD
```dax
Issues Created YTD = 
CALCULATE(
    [Total Issues],
    DATESYTD(DimDate[Date])
)
```

### SLA Compliance Rolling 3 Month
```dax
SLA Compliance Rolling 3M = 
CALCULATE(
    [SLA Compliance %],
    DATESINPERIOD(DimDate[Date], LASTDATE(DimDate[Date]), -3, MONTH)
)
```

---

## 6. Process Stage Duration Measures

*These measures require the IssueHistory table with ChangeTimestamp.*

### Avg Time in New Status (Hours)
```dax
Avg Time in New Hours = 
AVERAGEX(
    VALUES(IssueHistory[IssueId]),
    VAR NewEntry = 
        CALCULATE(
            MIN(IssueHistory[ChangeTimestamp]),
            IssueHistory[EventType] = "Created"
        )
    VAR AssignedEntry =
        CALCULATE(
            MIN(IssueHistory[ChangeTimestamp]),
            IssueHistory[EventType] = "Assigned"
        )
    RETURN
        IF(
            NOT ISBLANK(NewEntry) && NOT ISBLANK(AssignedEntry),
            DATEDIFF(NewEntry, AssignedEntry, MINUTE) / 60,
            BLANK()
        )
)
```

### Avg Time in Waiting Status (Hours)
```dax
Avg Time in Waiting Hours = 
AVERAGEX(
    FILTER(
        SUMMARIZE(IssueHistory, IssueHistory[IssueId]),
        CALCULATE(
            COUNTROWS(IssueHistory),
            IssueHistory[NewStatus] = "Waiting"
        ) > 0
    ),
    VAR WaitStart = 
        CALCULATE(
            MIN(IssueHistory[ChangeTimestamp]),
            IssueHistory[NewStatus] = "Waiting"
        )
    VAR WaitEnd =
        CALCULATE(
            MIN(IssueHistory[ChangeTimestamp]),
            IssueHistory[PreviousStatus] = "Waiting"
        )
    RETURN
        IF(
            NOT ISBLANK(WaitStart) && NOT ISBLANK(WaitEnd),
            DATEDIFF(WaitStart, WaitEnd, MINUTE) / 60,
            BLANK()
        )
)
```

---

## 7. Calculated Columns (Issues table)

These are defined as calculated columns, not measures:

### SLA Target Hours (Calculated Column)
```dax
SLA Target Hours = 
RELATED(SLARules[TargetHours])
```

### SLA Pct Consumed (Calculated Column)
```dax
SLAPctConsumed = 
VAR ElapsedHours = 
    DIVIDE(
        DATEDIFF(Issues[CreatedAt], 
            IF(Issues[ResolvedAt] <> BLANK(), Issues[ResolvedAt], NOW()),
            MINUTE),
        60
    )
RETURN
    IF(
        Issues[SLA Target Hours] <> BLANK() && Issues[SLA Target Hours] > 0,
        ROUND(DIVIDE(ElapsedHours, Issues[SLA Target Hours]) * 100, 1),
        BLANK()
    )
```

### Is SLA Breached (Calculated Column)
```dax
IsSLABreached = 
IF(
    Issues[SLADeadline] = BLANK(),
    FALSE(),
    IF(
        Issues[Status] IN {"Resolved", "Closed"},
        IF(Issues[ResolvedAt] <> BLANK(), Issues[ResolvedAt] > Issues[SLADeadline], FALSE()),
        NOW() > Issues[SLADeadline]
    )
)
```

### SLA Status Label (Calculated Column)
```dax
SLAStatusLabel = 
SWITCH(
    TRUE(),
    Issues[Status] IN {"Resolved", "Closed"} && NOT Issues[IsSLABreached], "Completed",
    Issues[IsSLABreached], "Breached",
    Issues[SLAPctConsumed] >= 90, "Critical",
    Issues[SLAPctConsumed] >= 70, "Warning",
    "Healthy"
)
```

### Resolution Duration Hours (Calculated Column)
```dax
ResolutionDurationHours = 
IF(
    Issues[ResolvedAt] <> BLANK(),
    DATEDIFF(Issues[CreatedAt], Issues[ResolvedAt], MINUTE) / 60,
    BLANK()
)
```

---

## 8. Naming Conventions

| Convention | Rule |
|------------|------|
| Measures | PascalCase with spaces: `Total Issues` |
| Calculated columns | PascalCase no spaces: `SLAPctConsumed` |
| Hidden columns | Prefixed with _ |
| Measure table | Named `_Measures` |
| Date table | Named `DimDate` |
| Lookup tables | Prefixed `Dim`: `DimDepartments` (optional) |
