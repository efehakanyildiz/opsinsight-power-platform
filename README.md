# OpsInsight — Operational Issue, SLA & Process Intelligence Platform

> **Portfolio Project** — Enterprise operational intelligence platform built on Microsoft Power Platform.  
> Fictional company: **Northstar Operations Group**

---

## Problem

Many organizations manage internal operational issues through fragmented tools — email, spreadsheets, Teams messages, and phone calls. This creates an operational blind spot where management cannot answer fundamental questions:

- How many active issues exist right now?
- Which teams are consistently missing SLA targets?
- At which stage of the process do issues stall?
- Are we becoming more efficient over time?

## Solution

OpsInsight is a centralized **Operational Intelligence Platform** that transforms daily operational activity into measurable process data.

**Core philosophy: Capture → Manage → Monitor → Analyze → Improve**

The system enables organizations to:
- Centralize issue capture across all departments
- Automatically route issues and enforce SLA policies
- Monitor real-time operational health
- Detect process bottlenecks from historical event data
- Support data-driven process improvement decisions

---

## Architecture

```
Employees / Agents / Managers
         │
         ▼
  Power Apps Canvas App
  (OpsInsight UI — role-based)
         │
         ▼
     Dataverse
  (Relational data store)
    /    │    \
   ▼     ▼     ▼
Power   Power   Power BI
Automate Automate Desktop
(Flows)  (Notifications) (Analytics)
   │               │
   ▼               ▼
Notifications  Operational
& Escalations  Intelligence
```

**Supporting development layer:**
- Python + Pandas → Synthetic data generation & validation
- SQL → Analytical reference queries & schema documentation
- Git/GitHub → Version control & portfolio presentation

---

## Key Features

### Operational Management
| Feature | Description |
|---------|-------------|
| Issue Capture | Structured submission with auto-routing |
| SLA Management | Configurable SLA rules by priority |
| Issue Lifecycle | 8-status workflow with full history |
| Team Queue | Priority-sorted agent workbench |
| Escalation | 2-level automatic escalation |
| Issue Timeline | Visual chronological event history |

### Process Intelligence
| Feature | Description |
|---------|-------------|
| Bottleneck Detection | Time-per-stage analysis |
| Root Cause Analysis | Categorized root cause tracking |
| SLA Performance | Compliance trends by department/category |
| Team Performance | Capacity and efficiency metrics |
| Reopen Rate | Recurring issue pattern detection |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Application | Microsoft Power Apps (Canvas App) |
| Database | Microsoft Dataverse |
| Automation | Microsoft Power Automate |
| Analytics | Microsoft Power BI Desktop |
| Query | Power Query (M) + DAX |
| Data Generation | Python 3.x + Pandas + Faker |
| Analytical Queries | SQL (PostgreSQL-compatible) |
| Version Control | Git + GitHub |

**Cost: £0** — All components use free developer/trial tiers.

---

## Business Value

| Outcome | Mechanism |
|---------|-----------|
| Centralized issue management | Single system replacing email/spreadsheet chaos |
| Reduced manual coordination | Auto-routing, notifications, escalations |
| Improved SLA compliance | Real-time SLA monitoring and alerts |
| Early risk identification | SLA warning thresholds before breach |
| Root cause visibility | Structured root cause capture and analysis |
| Bottleneck detection | Process stage duration analytics |
| Data-driven improvement | Historical trend analysis in Power BI |
| Full audit trail | Append-only IssueHistory event log |

---

## Data Model (Summary)

Core tables:

```
Departments ──< Teams ──< Employees
     │
     └──< IssueCategories
               │
               ▼
            Issues ──< IssueHistory (event log)
               │    ──< IssueComments
               │    ──< Escalations
               │
               ├── SLARules (by priority)
               ├── RootCauses
               └── ResolutionCodes
```

See [`docs/data-model.md`](docs/data-model.md) for full ERD and field definitions.

---

## Automation (Power Automate Flows)

| Flow | Trigger | Purpose |
|------|---------|---------|
| Issue Routing | New issue created | Auto-assign team + calculate SLA |
| High Priority Alert | Critical/High priority | Notify team + manager immediately |
| SLA Warning | Scheduled (hourly) | Flag issues at 70%+ SLA consumed |
| SLA Critical | Scheduled (hourly) | Escalate at 90%+ SLA consumed |
| SLA Breach | Scheduled (hourly) | Create escalation record + notify |
| Issue Resolution | Status → Resolved | Record resolution time + notify requester |
| Issue Reopen | Requester reopens | Increment counter + notify team |

---

## Analytics (Power BI — 5 Pages)

1. **Executive Overview** — Operational health KPIs and trends
2. **SLA Performance** — Compliance by department, category, priority
3. **Process Bottleneck Analysis** — Time spent per lifecycle stage
4. **Root Cause Analysis** — Recurring issues and resolution patterns
5. **Team Performance** — Capacity, workload, resolution metrics

---

## User Roles

| Role | Access |
|------|--------|
| Employee | Own issues only |
| Operations Agent | Team queue, issue management |
| Team Manager | Department issues, dashboards, SLA monitor |
| System Admin | Full configuration access |

---

## Screenshots

*(Power Platform screenshots require authenticated environment — see `/screenshots` directory after deployment)*

---

## How to Run

### 1. Generate Synthetic Data

```bash
cd python
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py
python validate_data.py
```

Generated CSVs appear in `data/generated/`.

### 2. Review SQL Scripts

```bash
# Review schema
cat sql/01_schema_reference.sql

# Run analytical queries (requires PostgreSQL or compatible engine)
psql -d your_db -f sql/02_operational_queries.sql
```

### 3. Power Platform Deployment

See [`docs/deployment-guide.md`](docs/deployment-guide.md) for:
- Dataverse table creation steps
- Power Apps import instructions
- Power Automate flow setup
- Power BI connection configuration

### 4. Power BI

- Open `power-bi/` directory
- Connect to CSV files in `data/generated/` for local testing
- See [`power-bi/report-design.md`](power-bi/report-design.md) for page-by-page design specification

---

## Project Structure

```
opsinsight/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── project-overview.md
│   ├── business-requirements.md
│   ├── architecture.md
│   ├── data-model.md
│   ├── power-apps-spec.md
│   ├── power-automate-spec.md
│   ├── power-bi-spec.md
│   ├── security-model.md
│   ├── deployment-guide.md
│   └── testing-plan.md
├── data/
│   ├── raw/
│   ├── generated/          ← CSV output files
│   └── processed/
├── python/
│   ├── generate_data.py    ← Main data generator
│   ├── validate_data.py    ← Data quality checker
│   └── requirements.txt
├── sql/
│   ├── 01_schema_reference.sql
│   ├── 02_operational_queries.sql
│   ├── 03_sla_analysis.sql
│   ├── 04_process_analysis.sql
│   └── 05_data_quality_checks.sql
├── power-platform/
│   ├── tables/             ← Dataverse table definitions
│   ├── flows/              ← Power Automate flow specs
│   ├── app/                ← Power Apps component specs
│   └── solution-notes/     ← Deployment notes
├── power-bi/
│   ├── data-dictionary.md
│   ├── measures.md
│   └── report-design.md
├── diagrams/
│   ├── architecture/
│   ├── erd/
│   └── process-flow/
└── screenshots/
```

---

## Future Improvements (V2)

- Microsoft Fabric / Lakehouse integration for large-scale analytics
- Microsoft Teams notifications via adaptive cards
- Business-hours-aware SLA calculation with holiday calendar
- Multi-company / multi-tenant architecture
- Advanced approval workflow integration
- Copilot Studio natural language interface
- Predictive SLA risk scoring

---

## CV Description

> **OpsInsight — Operational Intelligence Platform (Portfolio Project)**  
> Developed an end-to-end operational intelligence platform on Microsoft Power Platform (Power Apps, Dataverse, Power Automate, Power BI) to centralize internal issue management across 6 departments, automate SLA monitoring and escalation workflows, and provide real-time operational visibility for a fictional 120-person organization.  
>
> Designed process intelligence analytics using a historical issue event log (IssueHistory) to identify process bottlenecks, recurring root causes, and SLA performance trends across departments. Generated a realistic 2,000-issue synthetic dataset using Python/Pandas with intentional behavioral patterns to enable meaningful Power BI insights.

---

*Built as a portfolio/development project. No production deployment intended.*  
*All data is synthetic. No real personal data is used.*
