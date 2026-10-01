# OpsInsight — Testing Plan

**Version:** 1.0  
**Date:** October 2026  

---

## 1. Test Scope

This testing plan covers functional scenarios for OpsInsight V1.

Test categories:
1. Issue lifecycle
2. Auto-routing
3. SLA management
4. Priority handling
5. Notifications
6. Escalation
7. History creation
8. Data validation
9. Role-based access

---

## 2. Test Cases

---

### TC-001: Employee Creates Issue

**Category:** Issue Lifecycle  
**Priority:** Critical  

**Preconditions:**
- User is logged in as Employee role
- Finance department exists
- Reconciliation category exists

**Steps:**
1. Navigate to Create Issue screen
2. Enter title: "Invoice discrepancy in AP ledger"
3. Enter description (minimum 10 characters)
4. Select Department: Finance
5. Select Category: Reconciliation
6. Select Priority: High
7. Click Submit Issue

**Expected Results:**
- Issue record created in Dataverse
- Issue number generated (format: OPS-2026-XXXX)
- Status = "New" initially
- CreatedBy = current user
- CreatedAt = current timestamp

**Pass Criteria:** Issue appears in My Issues screen with correct IssueNumber.

---

### TC-002: Auto-Routing Assigns Correct Team

**Category:** Auto-Routing  
**Priority:** Critical  

**Preconditions:**
- TC-001 completed
- Finance → Reconciliation → DefaultTeam = Finance Operations

**Expected Results:**
- Power Automate flow triggers within 60 seconds
- Issue Status changes from "New" to "Assigned"
- AssignedTeamId = Finance Operations team ID
- SLADeadline populated
- IssueHistory record created: EventType = "Assigned"

**Pass Criteria:** AssignedTeamId matches Finance Operations, not manually set.

---

### TC-003: SLA Assignment by Priority

**Category:** SLA Management  
**Priority:** High  

**Steps:**
Create four issues with priorities: Critical, High, Medium, Low

**Expected Results:**

| Priority | SLA Target Hours | SLADeadline |
|----------|-----------------|-------------|
| Critical | 4 | CreatedAt + 4h |
| High | 8 | CreatedAt + 8h |
| Medium | 24 | CreatedAt + 24h |
| Low | 72 | CreatedAt + 72h |

**Pass Criteria:** All four SLADeadlines match expected calculation.

---

### TC-004: Agent Accepts and Updates Status

**Category:** Status Transitions  
**Priority:** High  

**Preconditions:**
- Issue in "Assigned" status
- Logged in as Agent in assigned team

**Steps:**
1. Navigate to Team Queue
2. Select issue
3. Change Status to "In Progress"
4. Submit

**Expected Results:**
- Issue Status = "In Progress"
- IssueHistory record created: EventType = "StatusChanged", PreviousStatus = "Assigned", NewStatus = "In Progress"
- FirstResponseAt populated (if null)
- LastUpdatedAt updated

**Pass Criteria:** History record exists with correct event type and timestamps.

---

### TC-005: Issue Placed in Waiting

**Category:** Status Transitions  
**Priority:** Medium  

**Steps:**
1. From "In Progress", agent changes status to "Waiting"
2. Adds note: "Waiting for manager approval"

**Expected Results:**
- Status = "Waiting"
- IssueHistory record: EventType = "StatusChanged", NewStatus = "Waiting"
- Note captured in history

**Pass Criteria:** Issue visible in SLA Monitor as an at-risk item.

---

### TC-006: Issue Resolved with Root Cause

**Category:** Issue Resolution  
**Priority:** Critical  

**Steps:**
1. Agent changes status to "Resolved"
2. Selects Root Cause: "Missing Approval"
3. Selects Resolution Code: "Process Updated"
4. Enters Resolution Summary

**Expected Results:**
- Status = "Resolved"
- ResolvedAt = current timestamp
- RootCauseId populated
- ResolutionCodeId populated
- IssueHistory: EventType = "Resolved"
- Email sent to issue creator

**Pass Criteria:** ResolvedAt is populated, root cause is recorded, history event exists.

---

### TC-007: Issue Closed by Requester

**Category:** Issue Lifecycle  
**Priority:** Medium  

**Steps:**
1. Requester views resolved issue
2. Clicks "Confirm Resolved / Close Issue"

**Expected Results:**
- Status = "Closed"
- ClosedAt = current timestamp
- ClosedAt >= ResolvedAt
- IssueHistory: EventType = "Closed"

**Pass Criteria:** ClosedAt populated, always after ResolvedAt.

---

### TC-008: Issue Reopened

**Category:** Reopen  
**Priority:** High  

**Preconditions:**
- Issue in "Resolved" status

**Steps:**
1. Requester clicks "Reopen Issue"
2. Adds note explaining why

**Expected Results:**
- Status = "Reopened"
- ReopenCount incremented by 1
- IssueHistory: EventType = "Reopened"
- Team notification sent

**Pass Criteria:** ReopenCount = 1 (for first reopen), history event created.

---

### TC-009: SLA Warning Notification

**Category:** SLA Monitoring  
**Priority:** High  

**Preconditions:**
- Issue with SLA at 70%+ consumed
- Issue still unresolved

**Steps:**
- Wait for scheduled SLA monitor flow (or manually trigger test)

**Expected Results:**
- SLA status field updated to "Warning"
- Email notification sent to Team Manager
- No duplicate notification sent on next run

**Pass Criteria:** Manager receives single warning email; SLA status = "Warning".

---

### TC-010: SLA Breach and Escalation

**Category:** SLA Breach  
**Priority:** Critical  

**Preconditions:**
- Issue SLADeadline < NOW()
- Issue still unresolved

**Expected Results:**
- SLA status = "Breached"
- Escalation record created in Escalations table
- EscalationLevel = 1
- Email sent to Team Manager
- IssueHistory: EventType = "Escalated"

**Pass Criteria:** Escalation record exists with EscalatedAt > SLADeadline.

---

### TC-011: Critical Issue Alert

**Category:** Notifications  
**Priority:** High  

**Steps:**
1. Create issue with Priority = "Critical"
2. Allow routing flow to complete

**Expected Results:**
- Email sent to Team Manager immediately upon assignment
- Subject contains "[URGENT]" and issue number
- Email sent within 2 minutes of issue creation

**Pass Criteria:** Email received promptly with correct content.

---

### TC-012: Team Queue Sorting

**Category:** Agent UX  
**Priority:** Medium  

**Expected Results:**
- Team Queue shows Critical issues first
- Within same priority, breached SLA issues appear before warning
- Resolved/Closed issues not shown

**Pass Criteria:** Visual queue matches sort specification.

---

### TC-013: SLA Monitor Shows Correct Issues

**Category:** SLA Monitor  
**Priority:** High  

**Expected Results:**
- Breached section: only issues where SLADeadline < NOW() and unresolved
- Critical: 90-100% consumed, unresolved
- Warning: 70-90% consumed, unresolved
- Healthy: <70% consumed

**Pass Criteria:** Each section contains only the correct issues.

---

### TC-014: Issue Timeline Displays Correctly

**Category:** Issue Details  
**Priority:** Medium  

**Steps:**
1. Open Issue Details for an issue with multiple history events

**Expected Results:**
- Timeline displays events in chronological order (oldest first)
- Each event shows: timestamp, event description, actor
- Waiting periods visible

**Pass Criteria:** Timeline matches IssueHistory table, sorted by ChangeTimestamp ASC.

---

### TC-015: Employee Cannot See Other Users' Issues

**Category:** Security  
**Priority:** Critical  

**Steps:**
1. Log in as Employee A
2. View My Issues

**Expected Results:**
- Only issues where CreatedBy = Employee A are visible
- No other employees' issues appear

**Pass Criteria:** Gallery filter correctly restricts to own issues.

---

### TC-016: Agent Cannot Access Administration

**Category:** Security  
**Priority:** High  

**Expected Results:**
- Administration navigation item not visible for Agent role
- Direct navigation to Admin screen shows access denied or is hidden

**Pass Criteria:** Navigation item invisible, screen inaccessible.

---

### TC-017: Issue Transfer Recorded

**Category:** Process Intelligence  
**Priority:** Medium  

**Steps:**
1. Agent transfers issue to different team

**Expected Results:**
- AssignedTeamId updated
- IssueHistory: EventType = "Transferred", PreviousTeam populated, NewTeam populated

**Pass Criteria:** Transfer event visible in issue timeline.

---

### TC-018: Data Quality — No Orphaned History

**Category:** Data Quality  
**Priority:** High  

**Steps:**
1. Run validate_data.py
2. Check "No orphaned IssueHistory" result

**Expected Results:**
- 0 orphaned history events

**Pass Criteria:** CHECK 14 passes in validation script.

---

### TC-019: Resolved Issues Have Root Cause

**Category:** Data Quality  
**Priority:** Medium  

**Steps:**
1. Attempt to resolve issue without selecting Root Cause

**Expected Results:**
- Application displays validation error
- Issue is not saved as Resolved without RootCauseId

**Pass Criteria:** Form validation prevents save without root cause.

---

### TC-020: Issue Number Format

**Category:** Data Integrity  
**Priority:** High  

**Expected Results:**
- All issue numbers follow format: OPS-YYYY-NNNN
- No duplicates
- Sequential numbering within year

**Pass Criteria:** validate_data.py CHECK 02 (No duplicate IssueNumbers) passes.

---

### TC-021: Manager Can View All Department Issues

**Category:** Security  
**Priority:** High  

**Steps:**
1. Log in as Finance Manager
2. View Team Queue / Dashboard

**Expected Results:**
- All Finance department issues visible
- Issues from IT/HR/Procurement not visible

**Pass Criteria:** Department filter applied correctly.

---

### TC-022: Admin Can Configure SLA Rules

**Category:** Administration  
**Priority:** Medium  

**Steps:**
1. Log in as Admin
2. Navigate to Administration → SLA Rules
3. Change Critical SLA from 4h to 6h
4. Create new issue with Critical priority

**Expected Results:**
- New critical issue has SLADeadline = CreatedAt + 6h (not 4h)

**Pass Criteria:** SLA rule change takes effect immediately for new issues.

---

## 3. Test Environment

| Requirement | Value |
|-------------|-------|
| Power Platform environment | Developer Plan |
| Test data | Synthetic CSV import |
| Roles to test | Employee, Agent, Manager, Admin |
| Browser | Microsoft Edge / Chrome |
| Email testing | Developer Outlook account |

---

## 4. Known Limitations (Development Environment)

| Limitation | Notes |
|------------|-------|
| Multi-user role testing | Single developer account — use conditional role variable |
| Power Automate email | Requires licensed Outlook connector |
| Power BI RLS | Not enforceable without Pro license |
| Real-time SLA updates | Dependent on Flow trigger frequency |
