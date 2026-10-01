# OpsInsight — Data Model & Data Dictionary

**Version:** 1.0  
**Date:** October 2026  

---

## 1. Entity Relationship Diagram

```
┌─────────────────┐
│   Departments   │
│─────────────────│
│ DepartmentId PK │◄──────────────────────────────┐
│ DepartmentName  │                               │
│ DepartmentCode  │                               │
│ Manager         │                               │
│ IsActive        │                               │
│ CreatedAt       │                               │
└────────┬────────┘                               │
         │ 1                                      │
         │                                        │
         │ ∞                                      │
┌────────▼────────┐        ┌────────────────────┐ │
│     Teams       │        │  IssueCategories   │ │
│─────────────────│        │────────────────────│ │
│ TeamId       PK │        │ CategoryId      PK │ │
│ TeamName        │◄───────│ DefaultTeamId   FK │ │
│ DepartmentId FK │────────►DepartmentId     FK ├─┘
│ TeamManager     │        │ CategoryName       │
│ IsActive        │        │ Description        │
└────────┬────────┘        │ IsActive           │
         │ 1               └────────┬───────────┘
         │                         │
         │ ∞                       │
┌────────▼────────┐                │
│   Employees     │                │
│─────────────────│                │
│ EmployeeId   PK │                │
│ EmployeeName    │                │
│ Email           │                │
│ DepartmentId FK │                │
│ TeamId       FK │                │
│ ManagerId    FK │                │
│ Role            │                │
│ IsActive        │                │
└────────┬────────┘                │
         │ ∞ (CreatedBy)           │ ∞
         │                ┌────────▼───────────────────────────────┐
         └───────────────►│              Issues                    │
                          │────────────────────────────────────────│
                          │ IssueId          PK                    │
                          │ IssueNumber      UNIQUE                │
                          │ Title                                  │
                          │ Description                            │
                          │ CreatedBy        FK→Employees          │
                          │ CreatedAt                              │
                          │ DepartmentId     FK→Departments        │
                          │ CategoryId       FK→IssueCategories    │
                          │ AssignedTeamId   FK→Teams              │
                          │ AssignedAgentId  FK→Employees          │
                          │ Priority         [Critical/High/       │
                          │                  Medium/Low]           │
                          │ Status           [New/Assigned/        │
                          │                  InProgress/Waiting/   │
                          │                  Resolved/Closed/      │
                          │                  Reopened/Cancelled]   │
                          │ SLAId            FK→SLARules           │
                          │ SLADeadline                            │
                          │ FirstResponseAt                        │
                          │ ResolvedAt                             │
                          │ ClosedAt                               │
                          │ RootCauseId      FK→RootCauses         │
                          │ ResolutionCodeId FK→ResolutionCodes    │
                          │ ResolutionSummary                      │
                          │ ReopenCount                            │
                          │ LastUpdatedAt                          │
                          └───────┬────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │ 1                 │ 1                 │ 1
              │ ∞                 │ ∞                 │ ∞
  ┌───────────▼───────┐  ┌───────▼────────┐  ┌──────▼────────┐
  │  IssueHistory     │  │ IssueComments  │  │  Escalations  │
  │───────────────────│  │────────────────│  │───────────────│
  │ HistoryId      PK │  │ CommentId   PK │  │ EscalationId  │
  │ IssueId        FK │  │ IssueId     FK │  │ IssueId    FK │
  │ EventType         │  │ CommentText    │  │ EscalationLv  │
  │ PreviousStatus    │  │ CommentAuthor  │  │ EscalatedTo   │
  │ NewStatus         │  │ CreatedAt      │  │ Reason        │
  │ PreviousTeam      │  │ IsInternal     │  │ EscalatedAt   │
  │ NewTeam           │  └────────────────┘  │ ResolvedAt    │
  │ ChangedBy         │                      └───────────────┘
  │ ChangeTimestamp   │
  │ Notes             │
  └───────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│    SLARules      │    │   RootCauses     │    │ ResolutionCodes  │
│──────────────────│    │──────────────────│    │──────────────────│
│ SLAId         PK │    │ RootCauseId   PK │    │ ResolutionCode PK│
│ Priority         │    │ RootCauseName    │    │ ResolutionName   │
│ TargetHours      │    │ CategoryId    FK │    │ Description      │
│ WarnThreshold%   │    │ Description      │    └──────────────────┘
│ CritThreshold%   │    └──────────────────┘
│ IsActive         │
└──────────────────┘
```

---

## 2. Data Dictionary

### 2.1 Departments

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| DepartmentId | GUID | Yes | Primary key | d1a2b3c4... |
| DepartmentName | Text(100) | Yes | Full department name | Information Technology |
| DepartmentCode | Text(10) | Yes | Short code | IT |
| Manager | Text(100) | No | Department manager name | Sarah Mitchell |
| IsActive | Boolean | Yes | Active flag | true |
| CreatedAt | DateTime | Yes | Record creation time | 2026-01-01T09:00:00 |

**Reference Data (6 departments):**

| Code | Name |
|------|------|
| IT | Information Technology |
| FIN | Finance |
| HR | Human Resources |
| PROC | Procurement |
| OPS | Operations |
| SALES | Sales Operations |

---

### 2.2 Teams

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| TeamId | GUID | Yes | Primary key | t1a2b3c4... |
| TeamName | Text(100) | Yes | Team display name | IT Applications |
| DepartmentId | GUID | Yes | FK → Departments | (Department GUID) |
| TeamManager | Text(100) | No | Manager name | James Roberts |
| IsActive | Boolean | Yes | Active flag | true |

**Reference Data (10 teams):**

| Team Name | Department |
|-----------|-----------|
| IT Applications | IT |
| IT Infrastructure | IT |
| Finance Operations | Finance |
| Accounts Payable | Finance |
| HR Operations | HR |
| Recruitment & Onboarding | HR |
| Procurement Operations | Procurement |
| Business Operations | Operations |
| Sales Operations Support | Sales Operations |
| Data & Reporting | Operations |

---

### 2.3 Employees

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| EmployeeId | GUID | Yes | Primary key | e1a2b3... |
| EmployeeName | Text(100) | Yes | Full name | Alex Johnson |
| Email | Text(150) | Yes | Corporate email | a.johnson@northstar.com |
| DepartmentId | GUID | Yes | FK → Departments | (GUID) |
| TeamId | GUID | No | FK → Teams | (GUID) |
| ManagerId | GUID | No | FK → Employees (self-ref) | (GUID) |
| Role | Text(50) | Yes | Employee/Agent/Manager/Admin | Employee |
| IsActive | Boolean | Yes | Active flag | true |

---

### 2.4 IssueCategories

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| CategoryId | GUID | Yes | Primary key | cat1a2... |
| CategoryName | Text(100) | Yes | Category display name | Application Error |
| DepartmentId | GUID | Yes | FK → Departments | (IT Dept GUID) |
| DefaultTeamId | GUID | Yes | FK → Teams (routing) | (IT Apps GUID) |
| Description | Text(500) | No | Category description | Software defects and errors |
| IsActive | Boolean | Yes | Active flag | true |

**Reference Categories:**

| Category | Department | Default Team |
|----------|-----------|--------------|
| Application Error | IT | IT Applications |
| Access Problem | IT | IT Applications |
| Reporting Problem | IT | IT Applications |
| Hardware | IT | IT Infrastructure |
| Integration | IT | IT Infrastructure |
| Invoice | Finance | Finance Operations |
| Payment | Finance | Finance Operations |
| Reconciliation | Finance | Finance Operations |
| Financial Reporting | Finance | Finance Operations |
| Payroll | HR | HR Operations |
| Leave Management | HR | HR Operations |
| Employee Records | HR | HR Operations |
| Onboarding | HR | Recruitment & Onboarding |
| Purchase Request | Procurement | Procurement Operations |
| Supplier Issue | Procurement | Procurement Operations |
| Contract | Procurement | Procurement Operations |
| Approval Delay | Procurement | Procurement Operations |
| Process Problem | Operations | Business Operations |
| Logistics | Operations | Business Operations |
| Capacity | Operations | Business Operations |
| Data Error | Operations | Data & Reporting |

---

### 2.5 Issues (Core Table)

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| IssueId | GUID | Yes | Primary key | iss1a2b... |
| IssueNumber | Text(20) | Yes | Human-readable ID (UNIQUE) | OPS-2026-0001 |
| Title | Text(200) | Yes | Short issue description | Invoice not posting in system |
| Description | Text(4000) | Yes | Detailed description | The November invoice for vendor ABC... |
| CreatedBy | GUID | Yes | FK → Employees | (Employee GUID) |
| CreatedAt | DateTime | Yes | Issue creation timestamp | 2026-03-15T10:22:00 |
| DepartmentId | GUID | Yes | FK → Departments | (Finance GUID) |
| CategoryId | GUID | Yes | FK → IssueCategories | (Invoice GUID) |
| AssignedTeamId | GUID | No | FK → Teams | (Finance Ops GUID) |
| AssignedAgentId | GUID | No | FK → Employees | (Agent GUID) |
| Priority | Choice | Yes | Critical / High / Medium / Low | High |
| Status | Choice | Yes | New / Assigned / In Progress / Waiting / Resolved / Closed / Reopened / Cancelled | Assigned |
| SLAId | GUID | No | FK → SLARules | (High SLA GUID) |
| SLADeadline | DateTime | No | Calculated SLA target | 2026-03-15T18:22:00 |
| FirstResponseAt | DateTime | No | Time of first agent action | 2026-03-15T10:35:00 |
| ResolvedAt | DateTime | No | Time issue marked Resolved | 2026-03-15T15:45:00 |
| ClosedAt | DateTime | No | Time issue marked Closed | 2026-03-15T16:00:00 |
| RootCauseId | GUID | No | FK → RootCauses | (Missing Approval GUID) |
| ResolutionCodeId | GUID | No | FK → ResolutionCodes | (Process Updated GUID) |
| ResolutionSummary | Text(2000) | No | Free-text resolution description | Approval workflow bypassed manually... |
| ReopenCount | Integer | Yes | Number of times reopened | 0 |
| LastUpdatedAt | DateTime | Yes | Last modification timestamp | 2026-03-15T15:45:00 |

**IssueNumber Format:** `OPS-{YYYY}-{NNNN}` — Year-sequential numbering.

**Priority Definitions:**

| Priority | Description | SLA Target |
|----------|-------------|-----------|
| Critical | Major business impact (e.g., payment system down) | 4 hours |
| High | Important operational impact (e.g., reconciliation failure) | 8 hours |
| Medium | Normal operational problem (e.g., report with wrong values) | 24 hours |
| Low | Minor / non-urgent (e.g., small interface issue) | 72 hours |

**Status Definitions:**

| Status | Description | Terminal? |
|--------|-------------|----------|
| New | Just submitted, not yet assigned | No |
| Assigned | Routed to team, not started | No |
| In Progress | Agent actively working | No |
| Waiting | Blocked — waiting for approval, info, or vendor | No |
| Resolved | Issue resolved by agent | No |
| Closed | Confirmed closed by requester or manager | Yes |
| Reopened | Requester unsatisfied, reopened | No |
| Cancelled | Issue cancelled — not applicable | Yes |

---

### 2.6 IssueHistory (Event Log)

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| HistoryId | GUID | Yes | Primary key | hist1a2... |
| IssueId | GUID | Yes | FK → Issues | (Issue GUID) |
| EventType | Text(50) | Yes | Type of event | StatusChanged |
| PreviousStatus | Text(50) | No | Status before change | Assigned |
| NewStatus | Text(50) | No | Status after change | In Progress |
| PreviousTeam | Text(100) | No | Team before transfer | IT Applications |
| NewTeam | Text(100) | No | Team after transfer | IT Infrastructure |
| ChangedBy | GUID | Yes | FK → Employees | (Agent GUID) |
| ChangeTimestamp | DateTime | Yes | When change occurred | 2026-03-15T10:35:00 |
| Notes | Text(1000) | No | Additional context | Started investigation |

**EventType Values:**

| EventType | Description |
|-----------|-------------|
| Created | Issue first submitted |
| Assigned | Team assigned |
| StatusChanged | Any status transition |
| PriorityChanged | Priority modified |
| Transferred | Moved to different team |
| Escalated | Escalation triggered |
| Resolved | Issue marked resolved |
| Closed | Issue closed |
| Reopened | Issue reopened |
| CommentAdded | Comment posted |

---

### 2.7 IssueComments

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| CommentId | GUID | Yes | Primary key | com1a2... |
| IssueId | GUID | Yes | FK → Issues | (Issue GUID) |
| CommentText | Text(2000) | Yes | Comment body | Checked the AP system — the invoice... |
| CommentAuthor | GUID | Yes | FK → Employees | (Agent GUID) |
| CreatedAt | DateTime | Yes | Comment timestamp | 2026-03-15T11:05:00 |
| IsInternal | Boolean | Yes | Internal-only flag | false |

---

### 2.8 SLARules

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| SLAId | GUID | Yes | Primary key | sla1a2... |
| Priority | Text(20) | Yes | Critical / High / Medium / Low | High |
| TargetHours | Decimal | Yes | Resolution target in hours | 8 |
| WarningThresholdPct | Integer | Yes | Warning trigger percentage | 70 |
| CriticalThresholdPct | Integer | Yes | Critical trigger percentage | 90 |
| IsActive | Boolean | Yes | Active flag | true |

**Default SLA Rules:**

| Priority | Target Hours | Warning % | Critical % |
|----------|-------------|-----------|-----------|
| Critical | 4 | 70 | 90 |
| High | 8 | 70 | 90 |
| Medium | 24 | 70 | 90 |
| Low | 72 | 70 | 90 |

---

### 2.9 Escalations

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| EscalationId | GUID | Yes | Primary key | esc1a2... |
| IssueId | GUID | Yes | FK → Issues | (Issue GUID) |
| EscalationLevel | Integer | Yes | 1 = Team Manager, 2 = Dept Manager | 1 |
| EscalatedTo | GUID | Yes | FK → Employees (manager) | (Manager GUID) |
| Reason | Text(500) | Yes | Escalation trigger reason | SLA breached — 4hr Critical issue unresolved |
| EscalatedAt | DateTime | Yes | Escalation creation time | 2026-03-15T14:22:00 |
| ResolvedAt | DateTime | No | When escalation was resolved | 2026-03-15T15:30:00 |

---

### 2.10 RootCauses

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| RootCauseId | GUID | Yes | Primary key | rc1a2b... |
| RootCauseName | Text(100) | Yes | Root cause label | Missing Approval |
| CategoryId | GUID | No | FK → IssueCategories (optional) | (Category GUID) |
| Description | Text(500) | No | Detailed explanation | Required approval was not obtained |

**Root Cause Reference Data:**

| Root Cause |
|-----------|
| Incorrect Configuration |
| Missing Approval |
| Data Quality |
| User Error |
| System Integration |
| Capacity |
| Vendor Dependency |
| Process Design |
| Missing Information |
| Access Rights |

---

### 2.11 ResolutionCodes

| Column | Data Type | Required | Description | Example |
|--------|-----------|----------|-------------|---------|
| ResolutionCodeId | GUID | Yes | Primary key | res1a2... |
| ResolutionName | Text(100) | Yes | Resolution label | Process Updated |
| Description | Text(500) | No | What was done | Approval workflow steps were revised |

**Resolution Code Reference Data:**

| Resolution Code |
|----------------|
| Configuration Updated |
| Data Corrected |
| User Guidance Provided |
| Process Updated |
| Access Granted |
| Vendor Resolved |
| Duplicate Request |
| No Action Required |
| Escalated to Third Party |

---

## 3. Relationship Summary

| Relationship | Cardinality | FK Location |
|-------------|-------------|-------------|
| Departments → Teams | 1:N | Teams.DepartmentId |
| Departments → Employees | 1:N | Employees.DepartmentId |
| Departments → IssueCategories | 1:N | IssueCategories.DepartmentId |
| Teams → Employees | 1:N | Employees.TeamId |
| Teams → IssueCategories | 1:N | IssueCategories.DefaultTeamId |
| Issues → IssueHistory | 1:N | IssueHistory.IssueId |
| Issues → IssueComments | 1:N | IssueComments.IssueId |
| Issues → Escalations | 1:N | Escalations.IssueId |
| Issues → Departments | N:1 | Issues.DepartmentId |
| Issues → IssueCategories | N:1 | Issues.CategoryId |
| Issues → Teams | N:1 | Issues.AssignedTeamId |
| Issues → Employees (created) | N:1 | Issues.CreatedBy |
| Issues → Employees (agent) | N:1 | Issues.AssignedAgentId |
| Issues → SLARules | N:1 | Issues.SLAId |
| Issues → RootCauses | N:1 | Issues.RootCauseId |
| Issues → ResolutionCodes | N:1 | Issues.ResolutionCodeId |
| RootCauses → IssueCategories | N:1 | RootCauses.CategoryId |

---

## 4. Indexes (Performance)

| Table | Index | Purpose |
|-------|-------|---------|
| Issues | Status, Priority | Team queue filtering |
| Issues | AssignedTeamId | Team-based lookup |
| Issues | CreatedBy | Employee "my issues" |
| Issues | SLADeadline | SLA monitoring |
| IssueHistory | IssueId | Timeline construction |
| IssueHistory | ChangeTimestamp | Chronological ordering |
| Escalations | IssueId | Issue escalation lookup |
