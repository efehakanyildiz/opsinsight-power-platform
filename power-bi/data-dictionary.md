# OpsInsight — Power BI Data Dictionary

**Version:** 1.0  
**Date:** October 2026  

---

## Tables in Semantic Model

| Table | Source | Description |
|-------|--------|-------------|
| Issues | issues.csv / Dataverse | Core transactional table |
| IssueHistory | issue_history.csv / Dataverse | Event log for process analytics |
| Departments | departments.csv / Dataverse | Department lookup |
| Teams | teams.csv / Dataverse | Team lookup |
| IssueCategories | categories.csv / Dataverse | Category lookup |
| SLARules | sla_rules.csv / Dataverse | SLA configuration |
| RootCauses | root_causes.csv / Dataverse | Root cause lookup |
| ResolutionCodes | resolution_codes.csv / Dataverse | Resolution type lookup |
| Escalations | escalations.csv / Dataverse | Escalation records |
| DimDate | Calculated in Power Query | Date dimension table |
| _Measures | Calculated | All DAX measures |

---

## Issues Table

| Column | Type | Description |
|--------|------|-------------|
| IssueId | Text | Primary key |
| IssueNumber | Text | Unique ticket number (OPS-YYYY-NNNN) |
| Title | Text | Short issue description |
| Description | Text | Full issue description |
| CreatedBy | Text | FK → Employees (EmployeeId) |
| CreatedByName | Text | Denormalized name |
| CreatedAt | DateTime | Issue submission timestamp |
| DepartmentId | Text | FK → Departments |
| DepartmentCode | Text | Denormalized code |
| CategoryId | Text | FK → IssueCategories |
| CategoryName | Text | Denormalized name |
| AssignedTeamId | Text | FK → Teams |
| AssignedTeamName | Text | Denormalized name |
| AssignedAgentId | Text | FK → Employees |
| AssignedAgentName | Text | Denormalized name |
| Priority | Text | Critical / High / Medium / Low |
| Status | Text | Current lifecycle status |
| SLAId | Text | FK → SLARules |
| SLATargetHours | Decimal | SLA hours from rule |
| SLADeadline | DateTime | Calculated deadline |
| FirstResponseAt | DateTime | First agent action timestamp |
| ResolvedAt | DateTime | Resolution timestamp |
| ClosedAt | DateTime | Close timestamp |
| RootCauseId | Text | FK → RootCauses |
| ResolutionCodeId | Text | FK → ResolutionCodes |
| ResolutionSummary | Text | Free-text resolution |
| ReopenCount | Integer | Number of reopens |
| LastUpdatedAt | DateTime | Last modification |

**Calculated columns added in Power Query:**
| Column | Description |
|--------|-------------|
| PriorityOrder | Integer sort key (Critical=1, Low=4) |
| IsResolved | Boolean — Resolved or Closed |
| IsSLABreached | Boolean — SLA was exceeded |
| CreatedMonth | Date — Start of creation month |
| CreatedYear | Integer |
| SLA Target Hours | From SLARules via RELATED() |
| SLAPctConsumed | % of SLA used |
| SLAStatusLabel | Healthy/Warning/Critical/Breached/Completed |
| ResolutionDurationHours | Hours from creation to resolution |

---

## IssueHistory Table

| Column | Type | Description |
|--------|------|-------------|
| HistoryId | Text | Primary key |
| IssueId | Text | FK → Issues |
| EventType | Text | Created/Assigned/StatusChanged/etc. |
| PreviousStatus | Text | Status before change |
| NewStatus | Text | Status after change |
| PreviousTeam | Text | Team before transfer |
| NewTeam | Text | Team after transfer |
| ChangedBy | Text | Employee ID or "SYSTEM" |
| ChangeTimestamp | DateTime | Event timestamp |
| Notes | Text | Additional context |

---

## DimDate Table

| Column | Type | Description |
|--------|------|-------------|
| Date | Date | Calendar date (primary key) |
| Year | Integer | Calendar year |
| Month | Integer | Month number (1-12) |
| MonthName | Text | "January" etc. |
| Quarter | Text | "Q1" etc. |
| Weekday | Text | "Monday" etc. |
| IsWeekend | Boolean | Saturday or Sunday |

---

## Key Measures Reference

| Measure | Description | Format |
|---------|-------------|--------|
| Total Issues | Count of all issues | Whole number |
| Open Issues | Issues in active statuses | Whole number |
| Resolved Issues | Resolved + Closed | Whole number |
| SLA Breached Issues | Count of breached | Whole number |
| SLA Compliance % | Resolved within SLA / Total resolved | % |
| Avg Resolution Time Hours | Mean hours to resolve | Decimal |
| Median Resolution Time Hours | Median hours | Decimal |
| Avg First Response Time Hours | Mean hours to first action | Decimal |
| Backlog | Currently unresolved | Whole number |
| Reopen Rate % | Reopened / Resolved | % |
| MoM Issue Change | This month vs last month | Whole number |
| MoM Issue Change % | % change month over month | % |
| Avg SLA Consumed % | Mean % of SLA used | % |
| Avg Transfers per Issue | Mean transfers | Decimal |
| Avg Status Changes per Issue | Mean events | Decimal |
| Avg Time in Waiting Hours | Mean hours in Waiting | Decimal |
| Issues Created YTD | Year-to-date created | Whole number |
| SLA Compliance Rolling 3M | Rolling 3-month compliance | % |

---

## Relationship Summary

| From | To | Type |
|------|----|------|
| DimDate[Date] | Issues[CreatedAt] (date) | 1:N |
| Departments[DepartmentId] | Issues[DepartmentId] | 1:N |
| Teams[TeamId] | Issues[AssignedTeamId] | 1:N |
| IssueCategories[CategoryId] | Issues[CategoryId] | 1:N |
| SLARules[SLAId] | Issues[SLAId] | 1:N |
| RootCauses[RootCauseId] | Issues[RootCauseId] | 1:N |
| ResolutionCodes[ResolutionCodeId] | Issues[ResolutionCodeId] | 1:N |
| Issues[IssueId] | IssueHistory[IssueId] | 1:N |
| Issues[IssueId] | Escalations[IssueId] | 1:N |
| Departments[DepartmentId] | Teams[DepartmentId] | 1:N |

All relationships: **Single** cross-filter direction, **Active**.

---

## Data Quality Notes

- Empty string timestamps treated as null in Power Query
- Priority sort uses PriorityOrder integer column
- SLAPctConsumed uses ResolvedAt if resolved, else NOW()
- IsSLABreached calculates against resolved timestamp if closed
- History table may have "SYSTEM" as ChangedBy — not a valid EmployeeId

---

## Report Slicers (Global)

| Slicer | Field | All Pages |
|--------|-------|-----------|
| Date Range | DimDate[Date] | Yes |
| Department | Departments[DepartmentName] | Yes |
| Priority | Issues[Priority] | Yes |
| Status | Issues[Status] | Yes |
