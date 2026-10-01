# OpsInsight — Power Automate Flow Specifications

**Version:** 1.0  
**Date:** October 2026  

---

## Overview

Seven automation flows support OpsInsight's operational logic. All flows use standard Power Automate connectors available in the free developer plan:
- **Microsoft Dataverse** connector
- **Office 365 Outlook** connector (email notifications)

No paid connectors are required.

---

## FLOW 1 — Issue Routing

**Name:** OpsInsight — Issue Routing  
**Trigger:** When a row is added (Dataverse — Issues table)  
**Purpose:** Auto-assign team, calculate SLA, create initial history record, notify team  

```
TRIGGER: When a new row is added to [Issues]
│
├─► Action: Get row (IssueCategories)
│   Input: CategoryId from trigger
│   Output: DefaultTeamId, CategoryName
│
├─► Action: Get row (SLARules)
│   Input: Filter: Priority = trigger.Priority AND IsActive = true
│   Output: TargetHours, SLAId
│
├─► Compose: Calculate SLA Deadline
│   Expression: addHours(triggerBody()?['CreatedAt'], outputs('Get_SLARule')?['TargetHours'])
│
├─► Action: Update row (Issues)
│   Fields:
│   - AssignedTeamId: DefaultTeamId
│   - SLAId: SLAId
│   - SLADeadline: [Calculated Deadline]
│   - Status: "Assigned"
│   - LastUpdatedAt: utcNow()
│
├─► Action: Add row (IssueHistory)
│   Fields:
│   - IssueId: trigger.IssueId
│   - EventType: "Created"
│   - NewStatus: "New"
│   - ChangedBy: trigger.CreatedBy
│   - ChangeTimestamp: trigger.CreatedAt
│   - Notes: "Issue submitted"
│
├─► Action: Add row (IssueHistory)
│   Fields:
│   - IssueId: trigger.IssueId
│   - EventType: "Assigned"
│   - PreviousStatus: "New"
│   - NewStatus: "Assigned"
│   - NewTeam: CategoryLookup.DefaultTeamId
│   - ChangedBy: "System"
│   - ChangeTimestamp: utcNow()
│   - Notes: "Auto-assigned based on category"
│
└─► Action: Send email (Office 365 Outlook)
    To: Team Manager email (lookup from Teams → Employees)
    Subject: [OpsInsight] New Issue Assigned — trigger.IssueNumber
    Body: 
      Issue: trigger.IssueNumber
      Title: trigger.Title
      Priority: trigger.Priority
      Category: CategoryName
      SLA Deadline: [Calculated Deadline]
      Please review in OpsInsight.
```

---

## FLOW 2 — High Priority Alert

**Name:** OpsInsight — High Priority Alert  
**Trigger:** When a row is modified (Dataverse — Issues table)  
**Condition:** Status changed to "Assigned" AND Priority = "Critical" OR "High"  
**Purpose:** Immediate notification for critical/high issues  

```
TRIGGER: When a row is modified (Issues)
│
├─► Condition: Priority is "Critical" OR "High"
│   AND Status = "Assigned" (just assigned)
│
├─► [YES Branch]
│   ├─► Get team details (Teams table)
│   │   Input: AssignedTeamId
│   │   Output: TeamManager name + email
│   │
│   ├─► Send email to Team Manager
│   │   Subject: [URGENT] OpsInsight — trigger.Priority Issue: trigger.IssueNumber
│   │   Body:
│   │     ⚠️ URGENT OPERATIONAL ISSUE
│   │     Issue Number: trigger.IssueNumber
│   │     Title: trigger.Title
│   │     Priority: trigger.Priority
│   │     Department: trigger.DepartmentId (resolved name)
│   │     SLA Deadline: trigger.SLADeadline
│   │     Please action immediately.
│   │
│   └─► Send email to Team members (optional: get team member list)
│
└─► [NO Branch] — Do nothing
```

---

## FLOW 3 — SLA Warning Monitor

**Name:** OpsInsight — SLA Warning Monitor  
**Trigger:** Recurrence — every 30 minutes  
**Purpose:** Detect issues approaching SLA warning threshold (70%)  

```
TRIGGER: Recurrence — every 30 minutes
│
├─► Action: List rows (Issues)
│   Filter: Status not in ('Resolved', 'Closed', 'Cancelled')
│
├─► Apply to each [Issue]
│   │
│   ├─► Get row (SLARules) by SLAId
│   │   Output: TargetHours, WarningThresholdPct
│   │
│   ├─► Compose: SLA% Consumed
│   │   Expression:
│   │   div(
│   │     mul(
│   │       div(
│   │         sub(ticks(utcNow()), ticks(item()?['CreatedAt'])),
│   │         36000000000
│   │       ),
│   │       100
│   │     ),
│   │     outputs('Get_SLARule')?['TargetHours']
│   │   )
│   │
│   ├─► Condition: SLA% >= WarningThresholdPct AND SLA% < CriticalThresholdPct
│   │   AND SLAStatus <> "Warning" (avoid duplicate notifications)
│   │
│   └─► [YES Branch]
│       ├─► Update row (Issues)
│       │   - SLAStatus: "Warning"
│       │
│       └─► Send email to Team Manager
│           Subject: [OpsInsight] SLA Warning — issue.IssueNumber
│           Body:
│             Issue issue.IssueNumber has consumed [SLA%]% of its SLA.
│             Title: issue.Title
│             Priority: issue.Priority
│             SLA Deadline: issue.SLADeadline
│             Please ensure timely resolution.
```

---

## FLOW 4 — SLA Critical Alert

**Name:** OpsInsight — SLA Critical Alert  
**Trigger:** Recurrence — every 30 minutes  
**Purpose:** Detect issues at 90%+ SLA consumed  

```
TRIGGER: Recurrence — every 30 minutes
│
├─► Action: List rows (Issues)
│   Filter: Status not in ('Resolved', 'Closed', 'Cancelled')
│          AND SLAStatus = "Warning" (already warned — escalate)
│
├─► Apply to each [Issue]
│   │
│   ├─► Calculate SLA% [same formula as Flow 3]
│   │
│   ├─► Condition: SLA% >= 90 AND SLA% < 100
│   │   AND SLAStatus <> "Critical" (no duplicate)
│   │
│   └─► [YES Branch]
│       ├─► Update row (Issues)
│       │   - SLAStatus: "Critical"
│       │
│       └─► Send email to Team Manager + Department Manager
│           Subject: [OpsInsight] ⚠️ SLA CRITICAL — issue.IssueNumber
│           Body:
│             URGENT: Issue issue.IssueNumber is approaching SLA breach.
│             SLA Consumed: [SLA%]%
│             Time Remaining: [calculated]
│             Immediate action required.
```

---

## FLOW 5 — SLA Breach Handler

**Name:** OpsInsight — SLA Breach Handler  
**Trigger:** Recurrence — every 30 minutes  
**Purpose:** Handle SLA breaches — create escalation, notify manager  

```
TRIGGER: Recurrence — every 30 minutes
│
├─► Action: List rows (Issues)
│   Filter: Status not in ('Resolved', 'Closed', 'Cancelled')
│          AND SLADeadline < utcNow()
│          AND SLAStatus <> "Breached" (avoid reprocessing)
│
├─► Apply to each [Issue]
│   │
│   ├─► Update row (Issues)
│   │   - SLAStatus: "Breached"
│   │
│   ├─► Add row (Escalations)
│   │   Fields:
│   │   - IssueId: item.IssueId
│   │   - EscalationLevel: 1
│   │   - EscalatedTo: [TeamManager lookup]
│   │   - Reason: "SLA Deadline exceeded for " + item.Priority + " issue"
│   │   - EscalatedAt: utcNow()
│   │
│   ├─► Add row (IssueHistory)
│   │   Fields:
│   │   - EventType: "Escalated"
│   │   - Notes: "SLA Breached — escalated to Team Manager"
│   │   - ChangedBy: "System"
│   │
│   └─► Send email to Team Manager
│       Subject: [OpsInsight] 🚨 SLA BREACHED — item.IssueNumber
│       Body:
│         ESCALATION REQUIRED
│         Issue item.IssueNumber has breached its SLA.
│         Priority: item.Priority
│         SLA Deadline was: item.SLADeadline
│         Current Status: item.Status
│         Assigned Agent: item.AssignedAgentId
│         Please escalate and ensure resolution immediately.
│
└─► Deduplication Note:
    SLAStatus field prevents re-sending breach notifications.
    Only issues where SLAStatus ≠ "Breached" are processed.
```

---

## FLOW 6 — Issue Resolution

**Name:** OpsInsight — Issue Resolution  
**Trigger:** When a row is modified (Issues table)  
**Condition:** Status changed to "Resolved"  
**Purpose:** Record resolution time, notify requester, create history  

```
TRIGGER: When a row is modified (Issues)
│
├─► Condition: Status = "Resolved"
│   AND Previous status ≠ "Resolved" (detect actual change)
│
├─► [YES Branch]
│   ├─► Compose: Resolution Duration (hours)
│   │   Expression: 
│   │   div(
│   │     sub(ticks(utcNow()), ticks(triggerBody()?['CreatedAt'])),
│   │     36000000000
│   │   )
│   │
│   ├─► Update row (Issues)
│   │   - ResolvedAt: utcNow()
│   │   - LastUpdatedAt: utcNow()
│   │
│   ├─► Add row (IssueHistory)
│   │   - EventType: "Resolved"
│   │   - PreviousStatus: [previous status]
│   │   - NewStatus: "Resolved"
│   │   - ChangeTimestamp: utcNow()
│   │   - Notes: "Issue resolved. Resolution: " + trigger.ResolutionSummary
│   │
│   └─► Send email to requester (CreatedBy)
│       To: [CreatedBy employee email lookup]
│       Subject: [OpsInsight] Issue Resolved — trigger.IssueNumber
│       Body:
│         Your issue has been resolved.
│         Issue: trigger.IssueNumber
│         Title: trigger.Title
│         Resolution: trigger.ResolutionSummary
│         Resolved by: trigger.AssignedAgentId (name lookup)
│         If you are not satisfied with the resolution, you may 
│         reopen this issue within 5 business days.
│
└─► [NO Branch] — Do nothing
```

---

## FLOW 7 — Issue Reopen

**Name:** OpsInsight — Issue Reopen  
**Trigger:** When a row is modified (Issues table)  
**Condition:** Status changed to "Reopened"  
**Purpose:** Track reopen event, notify team, update counter  

```
TRIGGER: When a row is modified (Issues)
│
├─► Condition: Status = "Reopened"
│
├─► [YES Branch]
│   ├─► Compose: New Reopen Count
│   │   Expression: add(triggerBody()?['ReopenCount'], 1)
│   │
│   ├─► Update row (Issues)
│   │   - ReopenCount: [New Reopen Count]
│   │   - Status: "Reopened"
│   │   - LastUpdatedAt: utcNow()
│   │
│   ├─► Add row (IssueHistory)
│   │   - EventType: "Reopened"
│   │   - PreviousStatus: "Resolved"
│   │   - NewStatus: "Reopened"
│   │   - ChangedBy: [CreatedBy — the requester]
│   │   - ChangeTimestamp: utcNow()
│   │   - Notes: "Issue reopened by requester"
│   │
│   └─► Send email to Assigned Team Manager
│       Subject: [OpsInsight] Issue Reopened — trigger.IssueNumber
│       Body:
│         The following issue has been reopened by the requester.
│         Issue: trigger.IssueNumber
│         Title: trigger.Title
│         Priority: trigger.Priority
│         Reopen Count: [New Reopen Count]
│         Please review and take action.
│
└─► [NO Branch] — Do nothing
```

---

## Flow Summary

| Flow | Trigger Type | Frequency | Notification Target |
|------|-------------|-----------|-------------------|
| Issue Routing | Dataverse (row added) | Real-time | Team Manager |
| High Priority Alert | Dataverse (row modified) | Real-time | Team Manager + Team |
| SLA Warning Monitor | Scheduled | Every 30 min | Team Manager |
| SLA Critical Alert | Scheduled | Every 30 min | Team + Dept Manager |
| SLA Breach Handler | Scheduled | Every 30 min | Team Manager |
| Issue Resolution | Dataverse (row modified) | Real-time | Issue Requester |
| Issue Reopen | Dataverse (row modified) | Real-time | Team Manager |

---

## Manual Setup Steps

1. Open Power Automate (make.powerautomate.com)
2. Create new flow for each spec above
3. Connect Microsoft Dataverse using your developer environment connection
4. Connect Office 365 Outlook for email notifications
5. Add error handling (scope + send email on failure) for scheduled flows
6. Test each flow using the "Test" function before activating
7. Enable all flows in Production mode

---

## Error Handling Notes

- All scheduled flows should have a **Scope (Run After: Has failed)** block to log failures
- Dataverse operations should include retry policies for transient failures
- Email actions should catch errors gracefully — flow should not fail if email delivery fails
- Implement **duplicate notification prevention** by checking SLAStatus field before sending
