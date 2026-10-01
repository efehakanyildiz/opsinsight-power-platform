# OpsInsight — Architecture Diagrams

---

## 1. System Architecture

```mermaid
graph TB
    subgraph Users["👥 Users"]
        EMP[Employee]
        AGT[Operations Agent]
        MGR[Team Manager]
        ADM[System Admin]
    end

    subgraph PowerApps["📱 Power Apps Canvas App — OpsInsight"]
        DASH[Dashboard]
        CREATE[Create Issue]
        MYISS[My Issues]
        QUEUE[Team Queue]
        SLA[SLA Monitor]
        INSIGHT[Process Insights]
        ADMIN[Administration]
    end

    subgraph Dataverse["🗄️ Microsoft Dataverse"]
        ISSUES[(Issues)]
        HISTORY[(IssueHistory)]
        COMMENTS[(IssueComments)]
        ESC[(Escalations)]
        LOOKUP[(Lookup Tables)]
    end

    subgraph Automate["⚡ Power Automate"]
        FLOW1[Issue Routing]
        FLOW2[High Priority Alert]
        FLOW3[SLA Warning]
        FLOW4[SLA Critical]
        FLOW5[SLA Breach]
        FLOW6[Resolution]
        FLOW7[Reopen]
    end

    subgraph Analytics["📊 Power BI"]
        PAGE1[Executive Overview]
        PAGE2[SLA Performance]
        PAGE3[Process Bottlenecks]
        PAGE4[Root Cause Analysis]
        PAGE5[Team Performance]
    end

    subgraph Support["🛠️ Supporting Layer"]
        PY[Python Data Generator]
        SQL[SQL Analytical Scripts]
        GIT[Git / GitHub]
    end

    EMP & AGT & MGR & ADM --> PowerApps
    PowerApps <--> Dataverse
    Dataverse --> Automate
    Automate --> EMAIL[📧 Email Notifications]
    Dataverse --> Analytics
    PY --> Dataverse
    SQL -.->|Reference| Dataverse
```

---

## 2. Issue Lifecycle Flow

```mermaid
stateDiagram-v2
    [*] --> New : Employee submits issue

    New --> Assigned : Auto-routing flow assigns team

    Assigned --> InProgress : Agent starts work

    InProgress --> Waiting : Blocked (approval / info needed)
    Waiting --> InProgress : Blocker resolved

    InProgress --> Resolved : Agent resolves issue
    Assigned --> Resolved : Direct resolution

    Resolved --> Closed : Requester confirms satisfaction
    Resolved --> Reopened : Requester unsatisfied

    Reopened --> InProgress : Agent resumes work
    Reopened --> Resolved : Re-resolved

    Assigned --> Cancelled : Issue withdrawn
    InProgress --> Cancelled : Issue cancelled

    Closed --> [*]
    Cancelled --> [*]
```

---

## 3. Entity Relationship Diagram

```mermaid
erDiagram
    DEPARTMENTS {
        uuid DepartmentId PK
        string DepartmentName
        string DepartmentCode
        string Manager
        bool IsActive
        datetime CreatedAt
    }

    TEAMS {
        uuid TeamId PK
        string TeamName
        uuid DepartmentId FK
        string TeamManager
        bool IsActive
    }

    EMPLOYEES {
        uuid EmployeeId PK
        string EmployeeName
        string Email
        uuid DepartmentId FK
        uuid TeamId FK
        uuid ManagerId FK
        string Role
        bool IsActive
    }

    ISSUE_CATEGORIES {
        uuid CategoryId PK
        string CategoryName
        uuid DepartmentId FK
        uuid DefaultTeamId FK
        string Description
        bool IsActive
    }

    SLA_RULES {
        uuid SLAId PK
        string Priority
        decimal TargetHours
        int WarningThresholdPct
        int CriticalThresholdPct
        bool IsActive
    }

    ROOT_CAUSES {
        uuid RootCauseId PK
        string RootCauseName
        uuid CategoryId FK
        string Description
    }

    RESOLUTION_CODES {
        uuid ResolutionCodeId PK
        string ResolutionName
        string Description
    }

    ISSUES {
        uuid IssueId PK
        string IssueNumber
        string Title
        text Description
        uuid CreatedBy FK
        datetime CreatedAt
        uuid DepartmentId FK
        uuid CategoryId FK
        uuid AssignedTeamId FK
        uuid AssignedAgentId FK
        string Priority
        string Status
        uuid SLAId FK
        datetime SLADeadline
        datetime FirstResponseAt
        datetime ResolvedAt
        datetime ClosedAt
        uuid RootCauseId FK
        uuid ResolutionCodeId FK
        int ReopenCount
        datetime LastUpdatedAt
    }

    ISSUE_HISTORY {
        uuid HistoryId PK
        uuid IssueId FK
        string EventType
        string PreviousStatus
        string NewStatus
        string PreviousTeam
        string NewTeam
        string ChangedBy
        datetime ChangeTimestamp
        text Notes
    }

    ISSUE_COMMENTS {
        uuid CommentId PK
        uuid IssueId FK
        text CommentText
        uuid CommentAuthor FK
        datetime CreatedAt
        bool IsInternal
    }

    ESCALATIONS {
        uuid EscalationId PK
        uuid IssueId FK
        int EscalationLevel
        uuid EscalatedTo FK
        text Reason
        datetime EscalatedAt
        datetime ResolvedAt
    }

    DEPARTMENTS ||--o{ TEAMS : "has"
    DEPARTMENTS ||--o{ EMPLOYEES : "employs"
    DEPARTMENTS ||--o{ ISSUE_CATEGORIES : "owns"
    TEAMS ||--o{ EMPLOYEES : "contains"
    TEAMS ||--o{ ISSUE_CATEGORIES : "handles"
    EMPLOYEES ||--o{ ISSUES : "creates"
    EMPLOYEES ||--o{ ISSUES : "handles"
    DEPARTMENTS ||--o{ ISSUES : "department"
    ISSUE_CATEGORIES ||--o{ ISSUES : "classifies"
    TEAMS ||--o{ ISSUES : "assigned"
    SLA_RULES ||--o{ ISSUES : "governs"
    ROOT_CAUSES ||--o{ ISSUES : "explains"
    RESOLUTION_CODES ||--o{ ISSUES : "resolves"
    ISSUES ||--o{ ISSUE_HISTORY : "tracks"
    ISSUES ||--o{ ISSUE_COMMENTS : "has"
    ISSUES ||--o{ ESCALATIONS : "triggers"
```

---

## 4. SLA Escalation Flow

```mermaid
flowchart TD
    A[Issue Created] --> B{Priority?}
    B -->|Critical| SLA4[SLA Target: 4 hours]
    B -->|High| SLA8[SLA Target: 8 hours]
    B -->|Medium| SLA24[SLA Target: 24 hours]
    B -->|Low| SLA72[SLA Target: 72 hours]

    SLA4 & SLA8 & SLA24 & SLA72 --> MONITOR

    MONITOR[Scheduled Monitor — every 30 min] --> CALC{Calculate\nSLA Consumed %}

    CALC -->|< 70%| HEALTHY[Status: Healthy\nNo action]
    CALC -->|70–90%| WARN[Status: Warning\nNotify Team Manager]
    CALC -->|90–100%| CRIT[Status: Critical\nNotify Team + Dept Manager]
    CALC -->|> 100%| BREACH[Status: Breached]

    BREACH --> ESC1[Create Escalation Record\nLevel 1: Team Manager]
    ESC1 --> NOTIFY_MGR[Send breach email\nto Team Manager]
    NOTIFY_MGR --> TRACK[IssueHistory Event:\nEventType = Escalated]

    RESOLVED{Issue\nResolved?} -->|Yes| DONE[Status: Completed\nCalculate Resolution Duration]
    RESOLVED -->|No| MONITOR
```

---

## 5. User Role Access Model

```mermaid
graph LR
    subgraph Roles
        EMP[Employee]
        AGT[Agent]
        MGR[Manager]
        ADM[Admin]
    end

    subgraph Data Access
        OWN[Own Issues]
        TEAM[Team Issues]
        DEPT[Department Issues]
        ALL[All Issues]
    end

    subgraph Features
        CREATE[Create Issue]
        QUEUE[Team Queue]
        SLA_MON[SLA Monitor]
        INSIGHTS[Process Insights]
        CONFIG[Administration]
    end

    EMP --> OWN
    EMP --> CREATE

    AGT --> TEAM
    AGT --> CREATE
    AGT --> QUEUE

    MGR --> DEPT
    MGR --> QUEUE
    MGR --> SLA_MON
    MGR --> INSIGHTS

    ADM --> ALL
    ADM --> CONFIG
    ADM --> SLA_MON
    ADM --> INSIGHTS
```

---

## 6. Data Pipeline

```mermaid
flowchart LR
    subgraph Generation
        PY[Python\ngenerate_data.py]
        CSV[CSV Files\n11 tables]
    end

    subgraph Storage
        DV[Microsoft\nDataverse]
    end

    subgraph Analytics
        PQ[Power Query\nTransformations]
        DAX[DAX\nMeasures]
        PBI[Power BI\nReports]
    end

    PY -->|Generates| CSV
    CSV -->|Import| DV
    DV -->|Dataverse connector| PQ
    CSV -.->|Local dev| PQ
    PQ --> DAX
    DAX --> PBI

    subgraph SQL
        SQL1[Schema Reference]
        SQL2[Operational Queries]
        SQL3[SLA Analysis]
        SQL4[Process Analysis]
        SQL5[Data Quality]
    end

    CSV -.->|Portfolio reference| SQL1
```
