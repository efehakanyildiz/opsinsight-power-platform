# OpsInsight — Dataverse Table Specifications

**Purpose:** Step-by-step reference for creating Dataverse tables manually.  
**Environment:** Power Apps Developer Plan  

---

## How to Create Tables

1. Go to [make.powerapps.com](https://make.powerapps.com)
2. Select your developer environment
3. Navigate to **Dataverse → Tables → + New table**
4. Choose **Create new table**

---

## Table 1: Departments

**Display Name:** Departments  
**Schema Name:** ops_Departments  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Department Name | ops_DepartmentName | Text (100) | Yes | Primary column |
| Department Code | ops_DepartmentCode | Text (10) | Yes | Short code (IT, FIN, HR) |
| Manager | ops_Manager | Text (100) | No | |
| Is Active | ops_IsActive | Yes/No | Yes | Default: Yes |
| Created At | ops_CreatedAt | Date and Time | Yes | |

---

## Table 2: Teams

**Display Name:** Teams  
**Schema Name:** ops_Teams  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Team Name | ops_TeamName | Text (100) | Yes | Primary column |
| Department | ops_DepartmentId | Lookup → Departments | Yes | |
| Team Manager | ops_TeamManager | Text (100) | No | |
| Is Active | ops_IsActive | Yes/No | Yes | Default: Yes |

---

## Table 3: Employees

**Display Name:** Employees  
**Schema Name:** ops_Employees  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Employee Name | ops_EmployeeName | Text (100) | Yes | Primary column |
| Email | ops_Email | Text (150) | Yes | |
| Department | ops_DepartmentId | Lookup → Departments | Yes | |
| Team | ops_TeamId | Lookup → Teams | No | |
| Manager | ops_ManagerId | Lookup → Employees | No | Self-reference |
| Role | ops_Role | Choice | Yes | Employee, Agent, Manager, Admin |
| Is Active | ops_IsActive | Yes/No | Yes | Default: Yes |

---

## Table 4: Issue Categories

**Display Name:** Issue Categories  
**Schema Name:** ops_IssueCategories  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Category Name | ops_CategoryName | Text (100) | Yes | Primary column |
| Department | ops_DepartmentId | Lookup → Departments | Yes | |
| Default Team | ops_DefaultTeamId | Lookup → Teams | Yes | Auto-routing |
| Description | ops_Description | Text Area (500) | No | |
| Is Active | ops_IsActive | Yes/No | Yes | Default: Yes |

---

## Table 5: SLA Rules

**Display Name:** SLA Rules  
**Schema Name:** ops_SLARules  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Priority | ops_Priority | Choice | Yes | Critical, High, Medium, Low |
| Target Hours | ops_TargetHours | Decimal | Yes | |
| Warning Threshold % | ops_WarningThresholdPct | Whole Number | Yes | Default: 70 |
| Critical Threshold % | ops_CriticalThresholdPct | Whole Number | Yes | Default: 90 |
| Is Active | ops_IsActive | Yes/No | Yes | Default: Yes |

---

## Table 6: Root Causes

**Display Name:** Root Causes  
**Schema Name:** ops_RootCauses  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Root Cause Name | ops_RootCauseName | Text (100) | Yes | Primary column |
| Category | ops_CategoryId | Lookup → IssueCategories | No | Optional |
| Description | ops_Description | Text Area (500) | No | |

---

## Table 7: Resolution Codes

**Display Name:** Resolution Codes  
**Schema Name:** ops_ResolutionCodes  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Resolution Name | ops_ResolutionName | Text (100) | Yes | Primary column |
| Description | ops_Description | Text Area (500) | No | |

---

## Table 8: Issues (Core Table)

**Display Name:** Issues  
**Schema Name:** ops_Issues  
**Enable auditing: YES**

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Issue Number | ops_IssueNumber | Text (20) | Yes | Auto-generated: OPS-YYYY-NNNN |
| Title | ops_Title | Text (200) | Yes | Primary column |
| Description | ops_Description | Text Area | Yes | |
| Created By | ops_CreatedBy | Lookup → Employees | Yes | |
| Created At | ops_CreatedAt | Date and Time | Yes | |
| Department | ops_DepartmentId | Lookup → Departments | Yes | |
| Category | ops_CategoryId | Lookup → IssueCategories | Yes | |
| Assigned Team | ops_AssignedTeamId | Lookup → Teams | No | |
| Assigned Agent | ops_AssignedAgentId | Lookup → Employees | No | |
| Priority | ops_Priority | Choice | Yes | Critical, High, Medium, Low |
| Status | ops_Status | Choice | Yes | New, Assigned, In Progress, Waiting, Resolved, Closed, Reopened, Cancelled |
| SLA Rule | ops_SLAId | Lookup → SLARules | No | |
| SLA Target Hours | ops_SLATargetHours | Decimal | No | |
| SLA Deadline | ops_SLADeadline | Date and Time | No | |
| SLA Status | ops_SLAStatus | Choice | No | Healthy, Warning, Critical, Breached, Completed |
| First Response At | ops_FirstResponseAt | Date and Time | No | |
| Resolved At | ops_ResolvedAt | Date and Time | No | |
| Closed At | ops_ClosedAt | Date and Time | No | |
| Root Cause | ops_RootCauseId | Lookup → RootCauses | No | |
| Resolution Code | ops_ResolutionCodeId | Lookup → ResolutionCodes | No | |
| Resolution Summary | ops_ResolutionSummary | Text Area | No | |
| Reopen Count | ops_ReopenCount | Whole Number | Yes | Default: 0 |
| Last Updated At | ops_LastUpdatedAt | Date and Time | Yes | |

---

## Table 9: Issue History

**Display Name:** Issue History  
**Schema Name:** ops_IssueHistory  
**Note:** Append-only. Never update records.

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Issue | ops_IssueId | Lookup → Issues | Yes | |
| Event Type | ops_EventType | Choice | Yes | Created, Assigned, StatusChanged, etc. |
| Previous Status | ops_PreviousStatus | Text (50) | No | |
| New Status | ops_NewStatus | Text (50) | No | |
| Previous Team | ops_PreviousTeam | Text (100) | No | |
| New Team | ops_NewTeam | Text (100) | No | |
| Changed By | ops_ChangedBy | Text (100) | Yes | Employee ID or "SYSTEM" |
| Change Timestamp | ops_ChangeTimestamp | Date and Time | Yes | |
| Notes | ops_Notes | Text Area | No | |

---

## Table 10: Issue Comments

**Display Name:** Issue Comments  
**Schema Name:** ops_IssueComments  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Issue | ops_IssueId | Lookup → Issues | Yes | |
| Comment Text | ops_CommentText | Text Area | Yes | |
| Author | ops_CommentAuthor | Lookup → Employees | Yes | |
| Created At | ops_CreatedAt | Date and Time | Yes | |
| Is Internal | ops_IsInternal | Yes/No | Yes | Default: No |

---

## Table 11: Escalations

**Display Name:** Escalations  
**Schema Name:** ops_Escalations  

| Display Name | Schema Name | Data Type | Required | Notes |
|-------------|-------------|-----------|----------|-------|
| Issue | ops_IssueId | Lookup → Issues | Yes | |
| Escalation Level | ops_EscalationLevel | Whole Number | Yes | 1 or 2 |
| Escalated To | ops_EscalatedTo | Lookup → Employees | Yes | |
| Reason | ops_Reason | Text Area | Yes | |
| Escalated At | ops_EscalatedAt | Date and Time | Yes | |
| Resolved At | ops_ResolvedAt | Date and Time | No | |

---

## Choice Field Values

### Priority (shared)
- Critical (value: 100)
- High (value: 200)
- Medium (value: 300)
- Low (value: 400)

### Status
- New (value: 1)
- Assigned (value: 2)
- In Progress (value: 3)
- Waiting (value: 4)
- Resolved (value: 5)
- Closed (value: 6)
- Reopened (value: 7)
- Cancelled (value: 8)

### SLA Status
- Healthy (value: 1)
- Warning (value: 2)
- Critical (value: 3)
- Breached (value: 4)
- Completed (value: 5)

### Role
- Employee (value: 1)
- Agent (value: 2)
- Manager (value: 3)
- Admin (value: 4)

### EventType (IssueHistory)
- Created
- Assigned
- StatusChanged
- PriorityChanged
- Transferred
- Escalated
- Resolved
- Closed
- Reopened
- CommentAdded
