# OpsInsight — Power Apps Specification

**Version:** 1.0  
**App Type:** Canvas App  
**Platform:** Microsoft Power Apps  

---

## 1. Application Overview

**App Name:** OpsInsight  
**Type:** Canvas App (single app, role-adaptive interface)  
**Target Devices:** Web browser (primary), tablet (secondary)  
**Connection:** Microsoft Dataverse  

The app displays a consistent navigation structure, but individual screens and navigation items adjust based on the logged-in user's role.

---

## 2. Visual Design System

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| Primary | #1B4FD8 | Primary buttons, active nav, accent |
| Primary Light | #EEF2FF | Highlighted backgrounds |
| Surface | #FFFFFF | Card and panel backgrounds |
| Background | #F8F9FA | Page background |
| Text Primary | #111827 | Headings and body |
| Text Secondary | #6B7280 | Labels and captions |
| Border | #E5E7EB | Dividers and card borders |
| Success | #16A34A | Resolved status |
| Warning | #D97706 | Warning SLA status |
| Danger | #DC2626 | Critical / Breached |
| Info | #2563EB | Assigned / In Progress |

### Status Badge Colors

| Status | Background | Text |
|--------|-----------|------|
| New | #DBEAFE | #1E40AF |
| Assigned | #E0E7FF | #3730A3 |
| In Progress | #D1FAE5 | #065F46 |
| Waiting | #FEF3C7 | #92400E |
| Resolved | #D1FAE5 | #065F46 |
| Closed | #F3F4F6 | #374151 |
| Reopened | #FFE4E6 | #9F1239 |
| Cancelled | #F3F4F6 | #6B7280 |

### Priority Badge Colors

| Priority | Background | Text |
|----------|-----------|------|
| Critical | #FEE2E2 | #DC2626 |
| High | #FEF3C7 | #D97706 |
| Medium | #DBEAFE | #1D4ED8 |
| Low | #F3F4F6 | #6B7280 |

### SLA Status Badge Colors

| SLA Status | Background | Text |
|-----------|-----------|------|
| Healthy | #D1FAE5 | #065F46 |
| Warning | #FEF3C7 | #92400E |
| Critical | #FEE2E2 | #991B1B |
| Breached | #4B0082 | #FFFFFF |
| Completed | #F3F4F6 | #374151 |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| App Title | Segoe UI | 20px | SemiBold |
| Screen Title | Segoe UI | 16px | SemiBold |
| Card Title | Segoe UI | 14px | Medium |
| Body | Segoe UI | 13px | Regular |
| Caption | Segoe UI | 11px | Regular |

---

## 3. Navigation Structure

### Left Navigation Panel (persistent)

Width: 220px  
Background: #1E293B (dark slate)  
Text: #CBD5E1  
Active item: #1B4FD8 left border + #EEF2FF text  

```
┌────────────────────┐
│ 🔷 OpsInsight      │  ← App logo + name
│────────────────────│
│   Dashboard        │  ← All roles
│   My Issues        │  ← Employee, Agent
│   Team Queue       │  ← Agent, Manager
│   Create Issue     │  ← Employee, Agent
│   SLA Monitor      │  ← Manager, Admin
│   Process Insights │  ← Manager, Admin
│   Administration   │  ← Admin only
│────────────────────│
│ 👤 Alex Johnson    │  ← Current user
│    Finance · Emp.  │  ← Dept + Role
└────────────────────┘
```

Navigation items are shown/hidden using:
```
Visible: If(UserRole = "Manager" || UserRole = "Admin", true, false)
```

---

## 4. Screen Specifications

---

### SCREEN 1: Home Dashboard

**Purpose:** First screen after login. Shows operational summary appropriate to user role.

**Employee View:**

```
┌─────────────────────────────────────────────────────┐
│ Good morning, Alex  ·  Thursday, 15 March 2026      │
│─────────────────────────────────────────────────────│
│ ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│ │Open Issues│  │Near SLA  │  │Resolved  │           │
│ │    3      │  │    1     │  │   12     │           │
│ └──────────┘  └──────────┘  └──────────┘           │
│                                                     │
│ ┌──────────────────────────────────────────────────┐│
│ │ + Create New Issue                    [Button]   ││
│ └──────────────────────────────────────────────────┘│
│                                                     │
│ Recent Issues                                       │
│ ┌────────────────────────────────────────────────┐  │
│ │ OPS-2026-0187  Invoice not posting  ●High ●SLA │  │
│ │ OPS-2026-0154  Access problem       ●Med  ●OK  │  │
│ │ OPS-2026-0101  Report incorrect     ●Low  ●OK  │  │
│ └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Manager View (additional section):**

```
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│ │Open Issues│ │SLA Breach│ │Avg Resol.│ │ Backlog  ││
│ │   47      │ │    3     │ │ 6.2 hrs  │ │   21     ││
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘│
│                                                      │
│ Critical Issues Requiring Attention                  │
│ ┌─────────────────────────────────────────────────┐ │
│ │ OPS-2026-0201 ●CRITICAL ●BREACHED  Finance Ops  │ │
│ │ OPS-2026-0198 ●HIGH     ●WARNING   IT Apps      │ │
│ └─────────────────────────────────────────────────┘ │
```

**Key Controls:**
- `KPI Cards`: Rectangle controls with label + number formula
- `Recent Issues Gallery`: Gallery control with filter by CreatedBy = CurrentUser
- `Create Issue Button`: NavigateToCreateIssue

---

### SCREEN 2: Create Issue

**Purpose:** Issue submission form. Clean, structured, guided.

```
┌───────────────────────────────────────────────────────┐
│ Create New Issue                                       │
│───────────────────────────────────────────────────────│
│ Title *                                               │
│ ┌─────────────────────────────────────────────────┐  │
│ │ Brief description of the issue...               │  │
│ └─────────────────────────────────────────────────┘  │
│                                                       │
│ Description *                                         │
│ ┌─────────────────────────────────────────────────┐  │
│ │ Detailed explanation...                         │  │
│ │                                                 │  │
│ └─────────────────────────────────────────────────┘  │
│                                                       │
│ Department *              Category *                  │
│ ┌──────────────────┐     ┌──────────────────────┐    │
│ │ Finance        ▼ │     │ Reconciliation      ▼ │    │
│ └──────────────────┘     └──────────────────────┘    │
│                                                       │
│ Priority *                                            │
│ ○ Critical  ● High  ○ Medium  ○ Low                  │
│                                                       │
│ Team (auto-assigned based on Category)               │
│ ┌─────────────────────────────────────────────────┐  │
│ │ Finance Operations  [Auto-assigned]             │  │
│ └─────────────────────────────────────────────────┘  │
│                                                       │
│              [Cancel]  [Submit Issue →]              │
└───────────────────────────────────────────────────────┘
```

**Submission Logic (OnSelect of Submit button):**

```
// 1. Validate required fields
If(
    IsBlank(txtTitle.Text) || IsBlank(ddDepartment.Selected.DepartmentId),
    Notify("Please complete all required fields", NotificationType.Error),

// 2. Create Issue record
    Patch(Issues,
        Defaults(Issues),
        {
            IssueNumber: "OPS-" & Text(Year(Now()), "0000") & "-" & 
                         Text(CountRows(Issues) + 1, "0000"),
            Title: txtTitle.Text,
            Description: txtDescription.Text,
            CreatedBy: LookUp(Employees, Email = User().Email, EmployeeId),
            CreatedAt: Now(),
            DepartmentId: ddDepartment.Selected.DepartmentId,
            CategoryId: ddCategory.Selected.CategoryId,
            Priority: rdPriority.Selected.Value,
            Status: "New",
            ReopenCount: 0,
            LastUpdatedAt: Now()
        }
    )
);
// 3. Trigger routing flow (via Power Automate button trigger or auto-flow)
```

**Validation Rules:**
- Title required, max 200 chars
- Department required
- Category required (filtered by selected department)
- Priority required (default: Medium)
- Description required, max 4000 chars

---

### SCREEN 3: My Issues

**Purpose:** Employee's issue list with filtering.

```
┌───────────────────────────────────────────────────────────┐
│ My Issues                              [+ Create Issue]   │
│───────────────────────────────────────────────────────────│
│ [All] [Open] [In Progress] [Waiting] [Resolved] [Closed] │
│───────────────────────────────────────────────────────────│
│ Ticket       Title                Status  Priority  SLA  │
│───────────────────────────────────────────────────────────│
│ OPS-2026-0187│Invoice not posting │●Waitng │●High   │⚠️Warn│
│ OPS-2026-0154│Access problem      │●InProg │●Medium │✓OK  │
│ OPS-2026-0101│Report incorrect    │●Closed │●Low    │✓Done│
│───────────────────────────────────────────────────────────│
│ (tap row to open Issue Details)                           │
└───────────────────────────────────────────────────────────┘
```

**Gallery Filter Formula:**
```
Filter(
    Issues,
    CreatedBy.EmployeeId = currentUserEmployee.EmployeeId,
    If(tabFilter.Selected.Value = "All", true,
    If(tabFilter.Selected.Value = "Open", Status = "New" || Status = "Assigned",
    Status = tabFilter.Selected.Value))
)
```

---

### SCREEN 4: Issue Details

**Purpose:** Full view of a single issue including timeline.

```
┌───────────────────────────────────────────────────────────┐
│ ← Back    OPS-2026-0187                    ●WAITING ●HIGH │
│───────────────────────────────────────────────────────────│
│ Invoice amount discrepancy in November reconciliation      │
│                                                           │
│ The November batch reconciliation shows a £12,400          │
│ discrepancy between the AP ledger and bank statement...   │
│                                                           │
│ ┌──────────────┬──────────────┬──────────────────────────┐│
│ │ Department   │ Category     │ Assigned Team            ││
│ │ Finance      │ Reconciliation│ Finance Operations      ││
│ ├──────────────┼──────────────┼──────────────────────────┤│
│ │ Created By   │ Created      │ SLA Deadline             ││
│ │ Alex Johnson │ 15 Mar 10:22 │ 15 Mar 18:22  ⚠️ Warning ││
│ └──────────────┴──────────────┴──────────────────────────┘│
│                                                           │
│ Timeline                                                  │
│ ─────────────────────────────────────────────────────     │
│  ● 10:22  Issue Created by Alex Johnson                   │
│  ● 10:28  Assigned to Finance Operations                  │
│  ● 10:41  Agent (James R.) started investigation          │
│  ● 12:15  Waiting — pending manager approval              │
│  ● 14:30  [current status]                                │
│                                                           │
│ Comments (2)                                              │
│ ─────────────────────────────────────────────────────     │
│ James R. · 10:41                                          │
│ Reviewing AP ledger entries now...                        │
│                                                           │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ Add comment...                            [Send]    │  │
│ └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

**Timeline Logic:**
```
// Gallery sorted by ChangeTimestamp ascending
SortByColumns(
    Filter(IssueHistory, IssueId = selectedIssue.IssueId),
    "ChangeTimestamp",
    SortOrder.Ascending
)
```

**Actions available (role-dependent):**
- Employee: Add comment, Request reopen (if Resolved)
- Agent: Change status, Add comment, Transfer team, Mark resolved
- Manager: Reassign, Escalate, Add internal comment

---

### SCREEN 5: Team Queue

**Purpose:** Operations Agent workbench. Priority-sorted issue queue.

```
┌───────────────────────────────────────────────────────────┐
│ Team Queue — Finance Operations          [12 open issues] │
│───────────────────────────────────────────────────────────│
│ Filter by: [Priority ▼] [Status ▼] [SLA Status ▼]        │
│ Sort by: [Priority + SLA] ▼                               │
│───────────────────────────────────────────────────────────│
│ ●CRITICAL ●BREACHED                                       │
│ OPS-2026-0201  Payment system posting failure             │
│ Finance · Payment · Assigned: Jane Smith  ⏱ 6h 23m ago   │
│ ─────────────────────────────────────────────────────     │
│ ●HIGH ●WARNING                                            │
│ OPS-2026-0187  Invoice amount discrepancy                 │
│ Finance · Reconciliation · Assigned: James R. ⏱ 4h 15m  │
│ ─────────────────────────────────────────────────────     │
│ ●MEDIUM ●HEALTHY                                          │
│ OPS-2026-0183  Supplier payment delayed                   │
│ Finance · Payment · Unassigned ⏱ 2h 30m                  │
└───────────────────────────────────────────────────────────┘
```

**Sort Formula:**
```
SortByColumns(
    Filter(Issues,
        AssignedTeamId = currentUserTeam.TeamId,
        Status <> "Resolved",
        Status <> "Closed",
        Status <> "Cancelled"
    ),
    "Priority", SortOrder.Ascending,  // Critical first (alphabetical won't work — use numeric sort key)
    "SLADeadline", SortOrder.Ascending  // Closest deadline first
)
```

*Note: Priority sort requires a numeric SortOrder field or calculated column.*

---

### SCREEN 6: SLA Monitor

**Purpose:** Manager view of all SLA risks in real time.

```
┌───────────────────────────────────────────────────────────┐
│ SLA Monitor                                               │
│───────────────────────────────────────────────────────────│
│ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ ┌────────┐ │
│ │  Breached   │ │  Critical   │ │  Warning  │ │Healthy │ │
│ │      3      │ │      7      │ │    11     │ │   26   │ │
│ └─────────────┘ └─────────────┘ └───────────┘ └────────┘ │
│───────────────────────────────────────────────────────────│
│ ●BREACHED                                                 │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ OPS-2026-0201  Payment failure  ●CRITICAL            │  │
│ │ Finance Ops · Jane Smith  ·  Elapsed: 7h 23m        │  │
│ │ Deadline: 15 Mar 14:00  [████████████] 183%         │  │
│ └─────────────────────────────────────────────────────┘  │
│                                                           │
│ ●CRITICAL                                                 │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ OPS-2026-0187  Reconciliation issue  ●HIGH           │  │
│ │ Finance Ops · James R.  ·  Elapsed: 4h 15m          │  │
│ │ Deadline: 15 Mar 18:22  [████████░░░░] 92%          │  │
│ └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

**SLA Percentage Formula (Power Apps):**
```
Round(
    (DateDiff(ThisItem.CreatedAt, Now(), TimeUnit.Minutes) /
     (LookUp(SLARules, Priority = ThisItem.Priority, TargetHours) * 60)) * 100,
    0
)
```

---

### SCREEN 7: Administration

**Purpose:** System Admin configuration screens. Simple tabbed layout.

**Tabs:**
- Departments
- Teams
- Categories
- SLA Rules
- Root Causes
- Resolution Codes

Each tab shows a simple editable gallery + Add/Edit/Deactivate buttons.

---

## 5. Variables & Collections

| Variable | Type | Purpose |
|----------|------|---------|
| currentUser | Record | Logged-in user from Employees table |
| currentUserRole | Text | Employee / Agent / Manager / Admin |
| currentUserTeam | Record | User's team record |
| selectedIssue | Record | Currently viewed issue |
| issuePriority | Text | For Create Issue form |
| issueCategory | Record | Selected category on Create form |

**OnStart (App):**
```
Set(currentUser, LookUp(Employees, Email = User().Email));
Set(currentUserRole, currentUser.Role);
Set(currentUserTeam, LookUp(Teams, TeamId = currentUser.TeamId));
```

---

## 6. Dataverse Connectors Required

| Connector | Permission |
|-----------|-----------|
| Issues | Read, Create, Update |
| IssueHistory | Read, Create |
| IssueComments | Read, Create |
| Employees | Read |
| Teams | Read |
| Departments | Read |
| IssueCategories | Read |
| SLARules | Read |
| Escalations | Read |
| RootCauses | Read |
| ResolutionCodes | Read |

---

## 7. Manual Deployment Steps

1. Create Dataverse tables per data-model.md specification
2. Import reference data (departments, teams, categories, SLA rules)
3. Create new Canvas App in Power Apps Studio
4. Add Dataverse as data source
5. Build screens following this specification
6. Configure role-based navigation using `currentUserRole` variable
7. Test all user role flows
8. Publish app and share with users
