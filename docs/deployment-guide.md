# OpsInsight — Deployment Guide

**Version:** 1.0  
**Target Environment:** Microsoft Power Apps Developer Plan (Free)

---

## Prerequisites

| Requirement | How to Get |
|-------------|-----------|
| Power Apps Developer Plan | [make.powerapps.com](https://make.powerapps.com) → Sign up free |
| Power BI Desktop | [Download free](https://powerbi.microsoft.com/desktop/) |
| Python 3.9+ | python.org |
| Git | git-scm.com |

---

## Phase 1: Generate Synthetic Data

```bash
# Clone repository
git clone https://github.com/[your-username]/opsinsight.git
cd opsinsight

# Set up Python environment
cd python
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate data
python generate_data.py

# Validate (should show 20/20 pass)
python validate_data.py
```

Generated files appear in `data/generated/`.

---

## Phase 2: Create Dataverse Environment

1. Go to [make.powerapps.com](https://make.powerapps.com)
2. Sign in with your Microsoft account (free)
3. Select your Developer environment (auto-created)
4. Navigate to: **Dataverse → Tables**

---

## Phase 3: Create Dataverse Tables

Create the following tables **in this order** (due to foreign key dependencies):

### Order of table creation:
1. `Departments`
2. `Teams` (requires Departments)
3. `Employees` (requires Departments + Teams)
4. `IssueCategories` (requires Departments + Teams)
5. `SLARules`
6. `RootCauses` (requires IssueCategories — optional FK)
7. `ResolutionCodes`
8. `Issues` (requires all above)
9. `IssueHistory` (requires Issues)
10. `IssueComments` (requires Issues + Employees)
11. `Escalations` (requires Issues + Employees)

### For each table:
- Reference [`docs/data-model.md`](data-model.md) for field definitions
- Use **Text** type for names and codes
- Use **Lookup** type for foreign key fields
- Use **Choice** type for Priority and Status (with defined values)
- Use **Date and Time** type for timestamp fields
- Enable **Auditing** on Issues table

### Choice Values to Define:

**Priority choices:**
- Critical
- High
- Medium
- Low

**Status choices:**
- New
- Assigned
- In Progress
- Waiting
- Resolved
- Closed
- Reopened
- Cancelled

**SLA Status choices:**
- Healthy
- Warning
- Critical
- Breached
- Completed

---

## Phase 4: Import Reference Data

Import CSVs to populate lookup tables:

1. Go to **Dataverse → Tables → [TableName] → Data**
2. Click **Import → Import data from Excel/CSV**
3. Import in this order:
   - departments.csv → Departments
   - teams.csv → Teams
   - sla_rules.csv → SLARules
   - root_causes.csv → RootCauses
   - resolution_codes.csv → ResolutionCodes
   - categories.csv → IssueCategories
   - employees.csv → Employees

*Note: issues.csv and issue_history.csv can be imported for demo data. For production, start with empty Issues table.*

---

## Phase 5: Create Power Automate Flows

1. Go to [make.powerautomate.com](https://make.powerautomate.com)
2. Create flows per [`docs/power-automate-spec.md`](power-automate-spec.md)
3. Test each flow using **Test → Manually trigger**
4. Enable flows in production mode

**Flows to create (in order):**
1. OpsInsight — Issue Routing
2. OpsInsight — High Priority Alert
3. OpsInsight — SLA Warning Monitor
4. OpsInsight — SLA Critical Alert
5. OpsInsight — SLA Breach Handler
6. OpsInsight — Issue Resolution
7. OpsInsight — Issue Reopen

---

## Phase 6: Create Power Apps Canvas App

1. Go to [make.powerapps.com](https://make.powerapps.com)
2. Create → **Canvas App from blank**
3. Name: `OpsInsight`
4. Format: Tablet (16:9)
5. Add Dataverse as data source
6. Build screens per [`docs/power-apps-spec.md`](power-apps-spec.md)

**Build order:**
1. App.OnStart (user role detection)
2. Left navigation panel
3. Home Dashboard
4. Create Issue form
5. My Issues list
6. Issue Details + Timeline
7. Team Queue
8. SLA Monitor
9. Administration

---

## Phase 7: Configure Power BI

1. Open Power BI Desktop
2. Get Data → Text/CSV
3. Load all CSVs from `data/generated/`
4. Apply Power Query transformations per [`docs/power-bi-spec.md`](power-bi-spec.md)
5. Create relationships per spec
6. Create `_Measures` table
7. Add all DAX measures from [`power-bi/measures.md`](../power-bi/measures.md)
8. Build report pages (5 pages)
9. Save as .pbix file

*Note: For Dataverse connection (instead of CSV), use Get Data → Dataverse and connect to your environment.*

---

## Phase 8: Configure Security

1. In Dataverse, create 4 security roles:
   - OpsInsight Employee
   - OpsInsight Agent
   - OpsInsight Manager
   - OpsInsight Admin

2. Assign permissions per [`docs/security-model.md`](security-model.md)

3. In Power Apps:
   - Share app with users
   - Assign appropriate security role

---

## Phase 9: Verify Deployment

Run through these verification steps:

- [ ] Create test issue as Employee → verify auto-routing
- [ ] Accept issue as Agent → verify status change + history
- [ ] Check SLA Monitor as Manager → verify calculation
- [ ] View Power BI Executive Overview → verify KPIs load
- [ ] Run validate_data.py → confirm 20/20 pass

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Flow not triggering | Check Dataverse trigger configuration; ensure Flow is enabled |
| SLA deadline blank | Verify SLARules table has data; check Priority field mapping in flow |
| Power Apps shows no data | Verify Dataverse connection + table permissions |
| Power BI blank | Check CSV file paths in Power Query; re-enter source paths |
| Email notifications failing | Verify Office 365 Outlook connection is authorized in Flow |

---

## Manual Steps Summary

These steps **cannot** be automated and must be done manually:

| Step | Location | Time Required |
|------|---------|--------------|
| Create Dataverse tables | make.powerapps.com | ~2 hours |
| Import CSV data | Dataverse import tool | ~30 min |
| Build Canvas App | Power Apps Studio | ~8 hours |
| Create Flow definitions | Power Automate | ~3 hours |
| Build Power BI report | Power BI Desktop | ~4 hours |
| Configure security roles | Dataverse admin | ~1 hour |

**Total estimated manual time: ~18 hours** (one-time setup)
