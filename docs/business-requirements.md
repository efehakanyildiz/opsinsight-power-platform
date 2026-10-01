# OpsInsight — Business Requirements Document

**Version:** 1.0  
**Date:** October 2026  
**Organization:** Northstar Operations Group (Fictional)  
**Project Type:** Portfolio / Development Environment  

---

## 1. Executive Summary

Northstar Operations Group is a fictional 120-person organization operating across 6 departments. Operational issues are currently managed through fragmented channels (email, spreadsheets, informal communication), resulting in missed SLA targets, lack of accountability, and inability to identify recurring process failures.

OpsInsight is proposed as a centralized **Operational Issue and Process Intelligence Platform** to replace fragmented management with a structured, data-driven system.

---

## 2. Business Problem Statement

### Current State

| Problem | Business Impact |
|---------|----------------|
| Issues tracked in email/spreadsheets | No single source of truth |
| No SLA enforcement | Missed deadlines go undetected |
| No assignment accountability | Issues fall through the cracks |
| No root cause tracking | Same problems recur repeatedly |
| No process analytics | Management lacks data for improvement |
| No historical audit trail | Cannot reconstruct issue timeline |

### Root Cause

The organization lacks a structured operational management system. Existing tools are communication platforms, not process management tools.

---

## 3. Business Objectives

| Priority | Objective |
|----------|-----------|
| P1 | Centralize all operational issue capture across departments |
| P1 | Enforce configurable SLA policies by issue priority |
| P1 | Create full audit trail of every issue lifecycle event |
| P2 | Automatically route issues to responsible teams |
| P2 | Alert managers before SLA breaches occur |
| P2 | Identify process bottlenecks from historical data |
| P3 | Enable root cause analysis and trend identification |
| P3 | Measure team performance and process efficiency |
| P3 | Support data-driven operational improvement decisions |

---

## 4. Scope

### In Scope (V1)

- Issue creation, management and lifecycle tracking
- Configurable SLA policy (by priority)
- Automatic issue routing (by category + department)
- 4 user roles with appropriate access controls
- Real-time SLA monitoring and alerting
- 2-level escalation workflow
- Full issue history (event log)
- Root cause and resolution code tracking
- Power BI analytics (5 report pages)
- Synthetic data generation for demo

### Out of Scope (V1 — Documented as V2)

- Business-hours-aware SLA calculation
- Microsoft Teams / Outlook native integration
- Predictive analytics / machine learning
- Microsoft Fabric integration
- Multi-company architecture
- External customer portal
- Advanced approval workflows
- Custom connectors

---

## 5. Functional Requirements

### FR-01 — Issue Management

| ID | Requirement |
|----|-------------|
| FR-01.1 | Users shall submit issues with title, description, department, category, and priority |
| FR-01.2 | System shall auto-generate unique issue numbers (format: OPS-YYYY-NNNN) |
| FR-01.3 | System shall support 8 issue statuses: New, Assigned, In Progress, Waiting, Resolved, Closed, Reopened, Cancelled |
| FR-01.4 | Every status change shall create an IssueHistory record |
| FR-01.5 | Issues shall support comments (internal and external) |
| FR-01.6 | Resolved issues shall capture root cause and resolution code |
| FR-01.7 | Users shall be able to reopen resolved issues |
| FR-01.8 | Reopen events shall increment a counter and create history record |

### FR-02 — Issue Routing

| ID | Requirement |
|----|-------------|
| FR-02.1 | System shall automatically determine assigned team based on category |
| FR-02.2 | Default team assignment shall be configurable per category |
| FR-02.3 | Operations Agents shall be able to transfer issues to other teams |
| FR-02.4 | All transfers shall be recorded in IssueHistory |

### FR-03 — SLA Management

| ID | Requirement |
|----|-------------|
| FR-03.1 | SLA targets shall be configurable by priority (not hardcoded) |
| FR-03.2 | System shall calculate SLA deadline at issue creation |
| FR-03.3 | System shall track: elapsed time, remaining time, % consumed |
| FR-03.4 | SLA statuses: Healthy (<70%), Warning (70-90%), Critical (90-100%), Breached (>100%), Completed |
| FR-03.5 | Warning and breach notifications shall be sent to responsible manager |
| FR-03.6 | SLA monitoring shall run on a scheduled basis |

### FR-04 — Escalation

| ID | Requirement |
|----|-------------|
| FR-04.1 | SLA breach shall automatically trigger Level 1 escalation (Team Manager) |
| FR-04.2 | Repeated breach or critical priority shall trigger Level 2 (Department Manager) |
| FR-04.3 | Escalation records shall be stored with timestamp and reason |
| FR-04.4 | Escalation notifications shall avoid duplicates |

### FR-05 — Notifications

| ID | Requirement |
|----|-------------|
| FR-05.1 | New critical/high issue → notify assigned team and manager |
| FR-05.2 | SLA warning threshold reached → notify team |
| FR-05.3 | SLA breach → notify manager |
| FR-05.4 | Issue resolved → notify issue creator |
| FR-05.5 | Issue reopened → notify assigned team |

### FR-06 — Analytics

| ID | Requirement |
|----|-------------|
| FR-06.1 | System shall provide executive overview of operational health |
| FR-06.2 | System shall display SLA compliance trends by department and category |
| FR-06.3 | System shall calculate average time spent per process stage |
| FR-06.4 | System shall identify top root causes by department and category |
| FR-06.5 | System shall show team performance metrics (issues assigned/resolved, SLA compliance) |

---

## 6. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Data integrity | No status change without IssueHistory record |
| Auditability | Full reconstruction of any issue timeline |
| Role security | Users see only records they are authorized to see |
| Cost | Zero paid dependencies in V1 |
| Data quality | Validated CSV exports with no orphaned foreign keys |

---

## 7. Assumptions

- Northstar Operations Group uses Microsoft 365
- Power Apps Developer Plan is available at no cost
- Dataverse developer environment is available
- Power BI Desktop is free for development
- All analytics are for internal reporting only (no paid Premium capacity required)
- Users access the system via web browser or Power Apps mobile

---

## 8. Stakeholders

| Role | Representative | Interest |
|------|---------------|----------|
| Executive Sponsor | CEO | Operational efficiency |
| Operations Director | Department Head | SLA compliance |
| Department Managers | 6 managers | Team visibility |
| Operations Agents | ~40 agents | Daily issue management |
| Employees | ~120 employees | Issue submission |
| IT Admin | System Admin | Configuration |
