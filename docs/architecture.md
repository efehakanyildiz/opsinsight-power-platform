# OpsInsight — System Architecture

**Version:** 1.0  
**Date:** October 2026  

---

## 1. Architecture Overview

OpsInsight follows a **Microsoft Power Platform** architecture pattern, appropriate for a mid-size organization using Microsoft 365.

The design follows a three-tier logical model:

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION TIER                      │
│                                                         │
│   Power Apps Canvas App (OpsInsight)                   │
│   Role-based navigation: Employee / Agent / Manager /   │
│   Admin                                                 │
└─────────────────────────┬───────────────────────────────┘
                          │ Dataverse Connector
┌─────────────────────────▼───────────────────────────────┐
│                    LOGIC / DATA TIER                     │
│                                                         │
│   Microsoft Dataverse                                   │
│   ├── Issues (core transactional table)                │
│   ├── IssueHistory (event log)                         │
│   ├── IssueComments                                    │
│   ├── Escalations                                      │
│   ├── Departments / Teams / Employees                  │
│   ├── IssueCategories                                  │
│   ├── SLARules                                         │
│   ├── RootCauses                                       │
│   └── ResolutionCodes                                  │
│                                                         │
│   Power Automate (Business Logic Layer)                 │
│   ├── Issue Routing Flow                               │
│   ├── High Priority Alert Flow                         │
│   ├── SLA Monitor Flows (Warning / Critical / Breach)  │
│   ├── Resolution Flow                                  │
│   └── Reopen Flow                                      │
└──────────┬──────────────────────────────────────────────┘
           │ 
┌──────────▼──────────────────────────────────────────────┐
│                  ANALYTICS TIER                          │
│                                                         │
│   Power BI Desktop                                      │
│   ├── Data Source: Dataverse (or CSV for local dev)    │
│   ├── Power Query (M): Data transformation             │
│   ├── DAX: Business measures                           │
│   └── 5 Report Pages:                                 │
│       1. Executive Overview                            │
│       2. SLA Performance                               │
│       3. Process Bottleneck Analysis                   │
│       4. Root Cause Analysis                           │
│       5. Team Performance                              │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Core Platform

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Application | Power Apps Canvas App | User interface (all roles) |
| Database | Microsoft Dataverse | Data storage and relationships |
| Automation | Power Automate | Business process automation |
| Analytics | Power BI Desktop | Operational intelligence |

### Development Support

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Generation | Python 3.x + Pandas + Faker | Synthetic demo dataset |
| Data Validation | Python 3.x | Data quality checks |
| Schema Documentation | SQL (PostgreSQL-compatible) | Relational reference model |
| Version Control | Git + GitHub | Repository management |

---

## 3. Data Flow

### Issue Creation Flow

```
Employee submits issue in Power Apps
    │
    ▼
Power Apps writes to Dataverse (Issues table)
    │
    ▼
Power Automate "Issue Routing" flow triggers
    │
    ├─► Lookup IssueCategory → get DefaultTeamId
    ├─► Lookup SLARules → match Priority → get TargetHours
    ├─► Calculate SLADeadline = CreatedAt + TargetHours
    ├─► Update Issue: AssignedTeamId, SLADeadline, Status=Assigned
    ├─► Create IssueHistory record (EventType: Created, Assigned)
    └─► Send notification to assigned team
```

### SLA Monitoring Flow

```
Scheduled trigger (every 30 minutes)
    │
    ▼
Query all unresolved Issues
    │
    ▼
For each issue:
    ├─► Calculate elapsed = NOW() - CreatedAt
    ├─► Calculate SLA% = elapsed / TargetHours × 100
    │
    ├─► If SLA% >= 100 → Mark Breached → Create Escalation → Notify Manager
    ├─► If SLA% >= 90  → Mark Critical → Notify Manager
    ├─► If SLA% >= 70  → Mark Warning  → Notify Team
    └─► Else           → Mark Healthy
```

### Analytics Flow

```
Dataverse (live) or CSV files (local dev)
    │
    ▼
Power Query (M)
    ├─► Type conversions
    ├─► Null handling
    ├─► Date normalization
    ├─► Table merges (lookups)
    └─► Calculated helper columns
    │
    ▼
Power BI Semantic Model
    ├─► Relationships defined
    └─► DAX measures calculated
    │
    ▼
Power BI Report Pages (5)
```

---

## 4. Security Architecture

### Row-Level Security (RLS) Design

| Role | Data Visibility |
|------|----------------|
| Employee | Issues WHERE CreatedBy = current user |
| Operations Agent | Issues WHERE AssignedTeamId = user's team |
| Team Manager | Issues WHERE DepartmentId = user's department |
| System Admin | All records |

### Power Platform Security

- Dataverse table-level permissions per role
- Column-level security for sensitive fields (e.g., internal comments)
- Power BI RLS applied at semantic model level
- Power Apps role-checked via User() function

---

## 5. Integration Points

| Integration | Status | Notes |
|------------|--------|-------|
| Dataverse ↔ Power Apps | Native | Primary connector |
| Dataverse ↔ Power Automate | Native | Trigger and action connectors |
| Dataverse ↔ Power BI | Native (Dataverse connector) | Live or import mode |
| Power Automate ↔ Email | Office 365 Outlook connector | Notification emails |
| CSV ↔ Power BI | File connector | Local development only |

---

## 6. Deployment Environment

| Environment | Purpose |
|------------|---------|
| Power Apps Developer Plan | Power Apps + Dataverse (free) |
| Power Automate (Developer) | Flow execution (free tier) |
| Power BI Desktop | Report design + local testing (free) |
| Python local | Data generation + validation |
| GitHub | Version control + portfolio |

---

## 7. Architecture Decisions

### ADR-01: Power Apps Canvas App vs Model-Driven App
**Decision:** Canvas App  
**Reason:** More flexible UI design; better for custom enterprise look-and-feel; supports complex multi-screen navigation with role-based visibility.

### ADR-02: Dataverse vs SQL Server / SharePoint
**Decision:** Dataverse  
**Reason:** Native Power Platform integration; built-in security model; no additional license cost in developer plan; proper relational model with foreign keys.

### ADR-03: V1 SLA Calculation (Calendar vs Business Hours)
**Decision:** Calendar time (V1)  
**Reason:** Business-hour calculation requires holiday calendar management and significantly increases complexity without proportional demo value. Documented as V2 enhancement.

### ADR-04: Python for Synthetic Data (not Power Apps with manual entry)
**Decision:** Python + Pandas  
**Reason:** Generating 2,000+ realistic issues with coherent history would be impractical through UI. Python enables controlled data patterns that produce meaningful Power BI insights.

### ADR-05: No Machine Learning in V1
**Decision:** Pure business logic for SLA status  
**Reason:** Transparent thresholds (70/90/100%) are more appropriate for a V1 operational system. ML would add complexity without proportional user benefit at this data scale.

---

## 8. Scalability Notes

This architecture is intentionally proportionate to a 120-person organization and demo scale.

For V2 at enterprise scale:

```
Dataverse
    │
    ▼
Microsoft Fabric / Lakehouse
    │
    ▼
Power BI Premium (direct lake mode)
    │
    ▼
Real-time operational dashboards
```
