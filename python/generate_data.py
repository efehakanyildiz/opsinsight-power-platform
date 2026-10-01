"""
OpsInsight — Synthetic Data Generator
======================================
Generates a realistic demo dataset for Northstar Operations Group.

Output files (in ../data/generated/):
  departments.csv
  teams.csv
  employees.csv
  categories.csv
  sla_rules.csv
  root_causes.csv
  resolution_codes.csv
  issues.csv
  issue_history.csv
  comments.csv
  escalations.csv

Design principles:
  - Realistic behavioral patterns per department
  - Intentional bottlenecks visible in Power BI
  - Chronologically consistent timestamps
  - FK integrity maintained throughout
  - Reproducible with fixed random seed

Usage:
  python generate_data.py
"""

import uuid
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

# ── Configuration ────────────────────────────────────────────────────────────

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
fake = Faker("en_GB")
fake.seed_instance(RANDOM_SEED)

START_DATE = datetime(2026, 1, 1, 9, 0, 0)
END_DATE   = datetime(2026, 9, 30, 18, 0, 0)

TARGET_ISSUES   = 2200
OUTPUT_DIR      = "../data/generated"

STATUSES        = ["New", "Assigned", "In Progress", "Waiting",
                   "Resolved", "Closed", "Reopened", "Cancelled"]
PRIORITIES      = ["Critical", "High", "Medium", "Low"]
EVENT_TYPES     = ["Created", "Assigned", "StatusChanged", "PriorityChanged",
                   "Transferred", "Escalated", "Resolved", "Closed",
                   "Reopened", "CommentAdded"]

# ── Reference Data ────────────────────────────────────────────────────────────

DEPARTMENTS_DATA = [
    {"DepartmentCode": "IT",    "DepartmentName": "Information Technology",  "Manager": "Sarah Mitchell"},
    {"DepartmentCode": "FIN",   "DepartmentName": "Finance",                  "Manager": "David Thompson"},
    {"DepartmentCode": "HR",    "DepartmentName": "Human Resources",          "Manager": "Emma Clarke"},
    {"DepartmentCode": "PROC",  "DepartmentName": "Procurement",              "Manager": "Robert Hughes"},
    {"DepartmentCode": "OPS",   "DepartmentName": "Operations",               "Manager": "Linda Foster"},
    {"DepartmentCode": "SALES", "DepartmentName": "Sales Operations",         "Manager": "Mark Patterson"},
]

TEAMS_DATA = [
    {"TeamName": "IT Applications",         "DepartmentCode": "IT",    "TeamManager": "James Roberts"},
    {"TeamName": "IT Infrastructure",       "DepartmentCode": "IT",    "TeamManager": "Rachel Green"},
    {"TeamName": "Finance Operations",      "DepartmentCode": "FIN",   "TeamManager": "Claire Watson"},
    {"TeamName": "Accounts Payable",        "DepartmentCode": "FIN",   "TeamManager": "Steven Adams"},
    {"TeamName": "HR Operations",           "DepartmentCode": "HR",    "TeamManager": "Natalie Brown"},
    {"TeamName": "Recruitment & Onboarding","DepartmentCode": "HR",    "TeamManager": "Peter Lawson"},
    {"TeamName": "Procurement Operations",  "DepartmentCode": "PROC",  "TeamManager": "Susan Taylor"},
    {"TeamName": "Business Operations",     "DepartmentCode": "OPS",   "TeamManager": "Daniel Cooper"},
    {"TeamName": "Sales Operations Support","DepartmentCode": "SALES", "TeamManager": "Helen Morris"},
    {"TeamName": "Data & Reporting",        "DepartmentCode": "OPS",   "TeamManager": "Chris Allen"},
]

CATEGORIES_DATA = [
    # IT
    {"CategoryName": "Application Error",  "DepartmentCode": "IT",   "DefaultTeam": "IT Applications"},
    {"CategoryName": "Access Problem",     "DepartmentCode": "IT",   "DefaultTeam": "IT Applications"},
    {"CategoryName": "Reporting Problem",  "DepartmentCode": "IT",   "DefaultTeam": "IT Applications"},
    {"CategoryName": "Hardware",           "DepartmentCode": "IT",   "DefaultTeam": "IT Infrastructure"},
    {"CategoryName": "Integration",        "DepartmentCode": "IT",   "DefaultTeam": "IT Infrastructure"},
    # Finance
    {"CategoryName": "Invoice",            "DepartmentCode": "FIN",  "DefaultTeam": "Finance Operations"},
    {"CategoryName": "Payment",            "DepartmentCode": "FIN",  "DefaultTeam": "Finance Operations"},
    {"CategoryName": "Reconciliation",     "DepartmentCode": "FIN",  "DefaultTeam": "Finance Operations"},
    {"CategoryName": "Financial Reporting","DepartmentCode": "FIN",  "DefaultTeam": "Finance Operations"},
    # HR
    {"CategoryName": "Payroll",            "DepartmentCode": "HR",   "DefaultTeam": "HR Operations"},
    {"CategoryName": "Leave Management",   "DepartmentCode": "HR",   "DefaultTeam": "HR Operations"},
    {"CategoryName": "Employee Records",   "DepartmentCode": "HR",   "DefaultTeam": "HR Operations"},
    {"CategoryName": "Onboarding",         "DepartmentCode": "HR",   "DefaultTeam": "Recruitment & Onboarding"},
    # Procurement
    {"CategoryName": "Purchase Request",   "DepartmentCode": "PROC", "DefaultTeam": "Procurement Operations"},
    {"CategoryName": "Supplier Issue",     "DepartmentCode": "PROC", "DefaultTeam": "Procurement Operations"},
    {"CategoryName": "Contract",           "DepartmentCode": "PROC", "DefaultTeam": "Procurement Operations"},
    {"CategoryName": "Approval Delay",     "DepartmentCode": "PROC", "DefaultTeam": "Procurement Operations"},
    # Operations
    {"CategoryName": "Process Problem",    "DepartmentCode": "OPS",  "DefaultTeam": "Business Operations"},
    {"CategoryName": "Logistics",          "DepartmentCode": "OPS",  "DefaultTeam": "Business Operations"},
    {"CategoryName": "Capacity",           "DepartmentCode": "OPS",  "DefaultTeam": "Business Operations"},
    {"CategoryName": "Data Error",         "DepartmentCode": "OPS",  "DefaultTeam": "Data & Reporting"},
    # Sales Operations
    {"CategoryName": "Sales Process",      "DepartmentCode": "SALES","DefaultTeam": "Sales Operations Support"},
    {"CategoryName": "CRM Issue",          "DepartmentCode": "SALES","DefaultTeam": "Sales Operations Support"},
    {"CategoryName": "Reporting",          "DepartmentCode": "SALES","DefaultTeam": "Sales Operations Support"},
]

SLA_RULES_DATA = [
    {"Priority": "Critical", "TargetHours": 4,  "WarningThresholdPct": 70, "CriticalThresholdPct": 90},
    {"Priority": "High",     "TargetHours": 8,  "WarningThresholdPct": 70, "CriticalThresholdPct": 90},
    {"Priority": "Medium",   "TargetHours": 24, "WarningThresholdPct": 70, "CriticalThresholdPct": 90},
    {"Priority": "Low",      "TargetHours": 72, "WarningThresholdPct": 70, "CriticalThresholdPct": 90},
]

ROOT_CAUSES_DATA = [
    "Incorrect Configuration", "Missing Approval", "Data Quality",
    "User Error", "System Integration", "Capacity", "Vendor Dependency",
    "Process Design", "Missing Information", "Access Rights",
]

RESOLUTION_CODES_DATA = [
    "Configuration Updated", "Data Corrected", "User Guidance Provided",
    "Process Updated", "Access Granted", "Vendor Resolved",
    "Duplicate Request", "No Action Required", "Escalated to Third Party",
]

# ── Behavioral parameters (per department) ────────────────────────────────────
# These create the intentional patterns visible in Power BI

DEPT_BEHAVIOR = {
    "IT": {
        "issue_weight": 0.28,       # More issues from IT
        "priority_dist": [0.12, 0.28, 0.40, 0.20],  # Crit/High/Med/Low
        "sla_breach_rate": 0.10,    # Moderate breach rate
        "waiting_probability": 0.20,
        "avg_waiting_hours": 3.0,
        "transfer_probability": 0.15,
        "reopen_probability": 0.08,
        "cancellation_probability": 0.03,
    },
    "FIN": {
        "issue_weight": 0.22,
        "priority_dist": [0.08, 0.30, 0.45, 0.17],
        "sla_breach_rate": 0.18,    # Higher — approval delays
        "waiting_probability": 0.45, # High waiting (approval process)
        "avg_waiting_hours": 9.0,    # Long waits
        "transfer_probability": 0.10,
        "reopen_probability": 0.10,
        "cancellation_probability": 0.02,
    },
    "HR": {
        "issue_weight": 0.15,
        "priority_dist": [0.03, 0.20, 0.55, 0.22],
        "sla_breach_rate": 0.08,
        "waiting_probability": 0.20,
        "avg_waiting_hours": 4.0,
        "transfer_probability": 0.08,
        "reopen_probability": 0.06,
        "cancellation_probability": 0.04,
    },
    "PROC": {
        "issue_weight": 0.18,
        "priority_dist": [0.05, 0.25, 0.50, 0.20],
        "sla_breach_rate": 0.22,    # Highest breach rate
        "waiting_probability": 0.60, # Very high — approval heavy
        "avg_waiting_hours": 14.0,   # Very long waits
        "transfer_probability": 0.12,
        "reopen_probability": 0.07,
        "cancellation_probability": 0.05,
    },
    "OPS": {
        "issue_weight": 0.12,
        "priority_dist": [0.06, 0.22, 0.52, 0.20],
        "sla_breach_rate": 0.12,
        "waiting_probability": 0.25,
        "avg_waiting_hours": 5.0,
        "transfer_probability": 0.10,
        "reopen_probability": 0.09,
        "cancellation_probability": 0.03,
    },
    "SALES": {
        "issue_weight": 0.05,
        "priority_dist": [0.04, 0.18, 0.58, 0.20],
        "sla_breach_rate": 0.08,
        "waiting_probability": 0.15,
        "avg_waiting_hours": 3.0,
        "transfer_probability": 0.08,
        "reopen_probability": 0.05,
        "cancellation_probability": 0.04,
    },
}

# Category-specific patterns that override department-level
CATEGORY_BEHAVIOR = {
    "Integration":       {"sla_breach_rate": 0.28, "avg_resolution_hours_multiplier": 2.5},
    "Approval Delay":    {"sla_breach_rate": 0.35, "avg_resolution_hours_multiplier": 2.0},
    "Reconciliation":    {"sla_breach_rate": 0.20, "avg_resolution_hours_multiplier": 1.8},
    "Data Error":        {"sla_breach_rate": 0.15, "avg_resolution_hours_multiplier": 1.5},
    "Application Error": {"sla_breach_rate": 0.08, "avg_resolution_hours_multiplier": 0.8},
    "Access Problem":    {"sla_breach_rate": 0.05, "avg_resolution_hours_multiplier": 0.5},
    "Payroll":           {"sla_breach_rate": 0.12, "avg_resolution_hours_multiplier": 1.3},
}

# ── Helper functions ──────────────────────────────────────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())

def random_dt(start: datetime, end: datetime) -> datetime:
    delta = end - start
    total = delta.total_seconds()
    if total <= 0 or (isinstance(total, float) and (total != total)):
        return start
    seconds = random.randint(0, int(total))
    return start + timedelta(seconds=seconds)

def add_hours(dt: datetime, hours: float) -> datetime:
    return dt + timedelta(hours=hours)

def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]

# ── Build reference tables ────────────────────────────────────────────────────

def build_departments():
    rows = []
    for d in DEPARTMENTS_DATA:
        rows.append({
            "DepartmentId":   new_id(),
            "DepartmentName": d["DepartmentName"],
            "DepartmentCode": d["DepartmentCode"],
            "Manager":        d["Manager"],
            "IsActive":       True,
            "CreatedAt":      "2026-01-01T09:00:00",
        })
    return pd.DataFrame(rows)

def build_teams(dept_df: pd.DataFrame):
    dept_map = dict(zip(dept_df["DepartmentCode"], dept_df["DepartmentId"]))
    rows = []
    for t in TEAMS_DATA:
        rows.append({
            "TeamId":         new_id(),
            "TeamName":       t["TeamName"],
            "DepartmentId":   dept_map[t["DepartmentCode"]],
            "DepartmentCode": t["DepartmentCode"],
            "TeamManager":    t["TeamManager"],
            "IsActive":       True,
        })
    return pd.DataFrame(rows)

def build_categories(dept_df: pd.DataFrame, team_df: pd.DataFrame):
    dept_map = dict(zip(dept_df["DepartmentCode"], dept_df["DepartmentId"]))
    team_map = dict(zip(team_df["TeamName"], team_df["TeamId"]))
    rows = []
    for c in CATEGORIES_DATA:
        rows.append({
            "CategoryId":     new_id(),
            "CategoryName":   c["CategoryName"],
            "DepartmentId":   dept_map[c["DepartmentCode"]],
            "DepartmentCode": c["DepartmentCode"],
            "DefaultTeamId":  team_map[c["DefaultTeam"]],
            "DefaultTeamName":c["DefaultTeam"],
            "Description":    f"Issues related to {c['CategoryName'].lower()}",
            "IsActive":       True,
        })
    return pd.DataFrame(rows)

def build_sla_rules():
    rows = []
    for s in SLA_RULES_DATA:
        rows.append({
            "SLAId":                  new_id(),
            "Priority":               s["Priority"],
            "TargetHours":            s["TargetHours"],
            "WarningThresholdPct":    s["WarningThresholdPct"],
            "CriticalThresholdPct":   s["CriticalThresholdPct"],
            "IsActive":               True,
        })
    return pd.DataFrame(rows)

def build_root_causes():
    rows = []
    for rc in ROOT_CAUSES_DATA:
        rows.append({
            "RootCauseId":   new_id(),
            "RootCauseName": rc,
            "Description":   f"Issue caused by {rc.lower()}",
        })
    return pd.DataFrame(rows)

def build_resolution_codes():
    rows = []
    for res in RESOLUTION_CODES_DATA:
        rows.append({
            "ResolutionCodeId": new_id(),
            "ResolutionName":   res,
            "Description":      f"Resolution: {res.lower()}",
        })
    return pd.DataFrame(rows)

def build_employees(dept_df: pd.DataFrame, team_df: pd.DataFrame):
    """Generate ~120 synthetic employees across departments."""
    dept_map = dict(zip(dept_df["DepartmentCode"], dept_df["DepartmentId"]))
    team_map = dict(zip(team_df["TeamName"], team_df["TeamId"]))
    team_dept_map = dict(zip(team_df["TeamName"], team_df["DepartmentCode"]))

    # Assign teams to departments with target employee counts
    team_targets = {
        "IT Applications":          12,
        "IT Infrastructure":         9,
        "Finance Operations":       10,
        "Accounts Payable":          8,
        "HR Operations":             9,
        "Recruitment & Onboarding":  6,
        "Procurement Operations":   10,
        "Business Operations":       8,
        "Sales Operations Support":  7,
        "Data & Reporting":          6,
    }

    employees = []
    manager_ids = {}

    # First create one Manager per team
    for team_name, count in team_targets.items():
        dept_code = team_dept_map[team_name]
        mgr_id = new_id()
        manager_ids[team_name] = mgr_id
        employees.append({
            "EmployeeId":   mgr_id,
            "EmployeeName": fake.name(),
            "Email":        fake.company_email(),
            "DepartmentId": dept_map[dept_code],
            "DepartmentCode": dept_code,
            "TeamId":       team_map[team_name],
            "TeamName":     team_name,
            "ManagerId":    None,
            "Role":         "Manager",
            "IsActive":     True,
        })

    # Create Agents (2/3 of team) and Employees (1/3)
    for team_name, count in team_targets.items():
        dept_code = team_dept_map[team_name]
        mgr_id = manager_ids[team_name]
        agent_count = max(2, int(count * 0.6))
        emp_count = count - agent_count

        for _ in range(agent_count):
            employees.append({
                "EmployeeId":     new_id(),
                "EmployeeName":   fake.name(),
                "Email":          fake.company_email(),
                "DepartmentId":   dept_map[dept_code],
                "DepartmentCode": dept_code,
                "TeamId":         team_map[team_name],
                "TeamName":       team_name,
                "ManagerId":      mgr_id,
                "Role":           "Agent",
                "IsActive":       True,
            })
        for _ in range(emp_count):
            employees.append({
                "EmployeeId":     new_id(),
                "EmployeeName":   fake.name(),
                "Email":          fake.company_email(),
                "DepartmentId":   dept_map[dept_code],
                "DepartmentCode": dept_code,
                "TeamId":         team_map[team_name],
                "TeamName":       team_name,
                "ManagerId":      mgr_id,
                "Role":           "Employee",
                "IsActive":       True,
            })

    # Add one System Admin
    employees.append({
        "EmployeeId":     new_id(),
        "EmployeeName":   "System Administrator",
        "Email":          "admin@northstar.com",
        "DepartmentId":   dept_map["IT"],
        "DepartmentCode": "IT",
        "TeamId":         team_map["IT Applications"],
        "TeamName":       "IT Applications",
        "ManagerId":      None,
        "Role":           "Admin",
        "IsActive":       True,
    })

    return pd.DataFrame(employees)

# ── Issue generation ──────────────────────────────────────────────────────────

ISSUE_TITLES = {
    "Application Error":   [
        "Application crashes on login", "Module throws 500 error",
        "UI not rendering correctly", "Data not saving in application",
        "Application timeout on bulk operation",
    ],
    "Access Problem":       [
        "User unable to access shared drive", "Permission denied on report portal",
        "Account locked out", "Missing access to Finance system",
        "Cannot login after password reset",
    ],
    "Reporting Problem":    [
        "Monthly report shows incorrect totals", "Report not generating",
        "Dashboard data stale", "Report filter not working",
        "Incorrect figures in weekly summary",
    ],
    "Hardware":             [
        "Laptop not connecting to docking station", "Printer offline",
        "Monitor flickering", "Keyboard unresponsive", "Network cable fault",
    ],
    "Integration":          [
        "API integration failing between systems", "Data sync not running",
        "ERP connector throwing errors", "Webhook not triggering",
        "Integration batch job failed",
    ],
    "Invoice":              [
        "Invoice not posting in system", "Duplicate invoice detected",
        "Invoice amount does not match PO", "Supplier invoice rejected",
        "Invoice approval stuck in workflow",
    ],
    "Payment":              [
        "Payment not processed for supplier", "Payment run failed",
        "Bank transfer rejected", "Payment posted to wrong account",
        "Duplicate payment raised",
    ],
    "Reconciliation":       [
        "Month-end reconciliation discrepancy", "Bank statement not matching ledger",
        "Intercompany reconciliation error", "Unreconciled items from previous period",
        "Reconciliation batch job failing",
    ],
    "Financial Reporting":  [
        "P&L report showing incorrect values", "Balance sheet out of balance",
        "Budget vs actual report not generating", "Management accounts delayed",
        "Reporting pack contains errors",
    ],
    "Payroll":              [
        "Payroll figures incorrect for March", "Bonus not included in payslip",
        "Tax code applied incorrectly", "Overtime not calculated",
        "Payroll run failed to complete",
    ],
    "Leave Management":     [
        "Annual leave balance incorrect", "Leave request not approved in system",
        "Holiday entitlement not showing", "Leave not deducted from balance",
        "Leave approval workflow stuck",
    ],
    "Employee Records":     [
        "Employee details not updated in HRIS", "Wrong department on employee record",
        "Contract end date incorrect", "Job title not reflecting promotion",
        "Employee missing from payroll system",
    ],
    "Onboarding":           [
        "New starter equipment not ready", "System access not provisioned",
        "Induction checklist incomplete", "Training not assigned to new starter",
        "Badge access not set up",
    ],
    "Purchase Request":     [
        "Purchase request not approved", "PO not generated from approved PR",
        "Budget code missing on purchase request", "Supplier not on approved list",
        "PR stuck in approval workflow",
    ],
    "Supplier Issue":       [
        "Supplier delivery delayed", "Supplier quality issue",
        "Supplier unresponsive", "Wrong goods delivered",
        "Supplier invoice dispute",
    ],
    "Contract":             [
        "Contract renewal not processed", "Contract terms not updated",
        "Supplier contract expired", "Contract missing from system",
        "Contract approval delayed",
    ],
    "Approval Delay":       [
        "PO approval waiting for 3 days", "Budget approval stuck with director",
        "Capex approval not processed", "Approval chain broken in system",
        "Manager approval not received",
    ],
    "Process Problem":      [
        "Operational process not followed", "Handover process breaking down",
        "Standard operating procedure outdated", "Process gap identified",
        "Step missing from current workflow",
    ],
    "Logistics":            [
        "Shipment delayed at distribution centre", "Incorrect routing for delivery",
        "Goods not arrived as scheduled", "Logistics provider unresponsive",
        "Tracking information not updating",
    ],
    "Capacity":             [
        "Team at capacity — unable to take new work", "Resource shortage identified",
        "Capacity constraint affecting delivery", "Workload imbalance across team",
        "Overtime required due to capacity gap",
    ],
    "Data Error":           [
        "Incorrect data in reporting database", "Data transformation error in pipeline",
        "Master data not updated correctly", "Duplicate records in database",
        "Data quality check failed",
    ],
    "Sales Process":        [
        "Sales order not converted to contract", "Pricing error on sales quote",
        "CRM stage not updating", "Commission calculation incorrect",
        "Sales pipeline data inaccurate",
    ],
    "CRM Issue":            [
        "CRM not syncing with ERP", "Duplicate accounts in CRM",
        "Opportunity stage stuck", "CRM report not generating",
        "Contact record missing from CRM",
    ],
    "Reporting":            [
        "Sales dashboard showing wrong figures", "Weekly report not distributed",
        "KPI report missing data", "Forecasting report error",
        "Territory report not filtering correctly",
    ],
}

# Root cause weights per category
ROOT_CAUSE_WEIGHTS = {
    "Application Error":   [5,1,3,8,4,1,2,2,3,1],  # User Error, Data Quality heavy
    "Access Problem":      [1,2,1,5,1,1,1,1,2,8],  # Access Rights heavy
    "Reporting Problem":   [2,1,8,3,1,1,1,2,2,1],  # Data Quality heavy
    "Hardware":            [3,1,1,4,2,2,3,2,2,1],
    "Integration":         [4,1,2,2,9,1,3,3,2,1],  # System Integration heavy
    "Invoice":             [1,5,4,2,1,1,1,3,5,1],  # Missing Approval, Data Quality
    "Payment":             [2,6,3,2,1,2,3,3,2,1],  # Missing Approval
    "Reconciliation":      [3,4,7,2,2,1,1,2,4,1],  # Data Quality, Missing Approval
    "Financial Reporting": [2,3,6,2,3,1,1,3,3,1],
    "Payroll":             [2,3,5,3,2,1,1,2,4,1],
    "Leave Management":    [1,2,2,5,1,1,1,3,3,1],
    "Employee Records":    [1,1,5,4,1,1,1,2,4,1],
    "Onboarding":          [2,3,2,3,2,1,1,5,5,2],  # Process Design, Missing Info
    "Purchase Request":    [1,8,2,2,1,1,2,4,4,1],  # Missing Approval heavy
    "Supplier Issue":      [1,2,2,2,1,3,8,2,2,1],  # Vendor Dependency heavy
    "Contract":            [1,5,2,1,1,1,3,3,4,1],
    "Approval Delay":      [1,9,1,1,1,1,1,4,3,1],  # Missing Approval dominant
    "Process Problem":     [2,2,3,3,2,3,1,8,3,1],  # Process Design heavy
    "Logistics":           [1,1,2,2,1,3,6,3,2,1],  # Vendor Dependency
    "Capacity":            [1,1,1,1,1,9,1,3,2,1],  # Capacity heavy
    "Data Error":          [3,1,9,3,2,1,1,2,3,1],  # Data Quality dominant
    "Sales Process":       [2,2,3,4,1,1,1,4,3,1],
    "CRM Issue":           [4,1,3,3,5,1,1,2,2,1],  # Config, Integration
    "Reporting":           [2,1,5,3,2,1,1,2,3,1],
}

def generate_issues(
    dept_df, team_df, cat_df, sla_df, emp_df, root_cause_df, resolution_code_df
):
    """Generate the main issues dataset with realistic patterns."""

    sla_map = dict(zip(sla_df["Priority"], sla_df["SLAId"]))
    sla_hours = dict(zip(sla_df["Priority"], sla_df["TargetHours"]))

    dept_ids   = dict(zip(dept_df["DepartmentCode"], dept_df["DepartmentId"]))
    dept_codes = list(dept_df["DepartmentCode"])
    dept_weights = [DEPT_BEHAVIOR[c]["issue_weight"] for c in dept_codes]

    root_cause_ids   = list(root_cause_df["RootCauseId"])
    root_cause_names = list(root_cause_df["RootCauseName"])
    res_code_ids     = list(resolution_code_df["ResolutionCodeId"])

    # Prepare team and category lookups
    team_by_id   = team_df.set_index("TeamId").to_dict("index")
    cat_by_id    = cat_df.set_index("CategoryId").to_dict("index")
    cats_by_dept = cat_df.groupby("DepartmentCode")

    # Employee lookups
    agents_by_team = emp_df[emp_df["Role"] == "Agent"].groupby("TeamId")
    reporters_by_dept = emp_df[emp_df["Role"] == "Employee"].groupby("DepartmentCode")

    issues = []
    issue_counter = 1

    for _ in range(TARGET_ISSUES):
        dept_code = weighted_choice(dept_codes, dept_weights)
        behavior  = DEPT_BEHAVIOR[dept_code]

        dept_id = dept_ids[dept_code]

        # Pick category from department
        dept_cats = cats_by_dept.get_group(dept_code)
        cat_row   = dept_cats.sample(1).iloc[0]
        cat_id    = cat_row["CategoryId"]
        cat_name  = cat_row["CategoryName"]
        team_id   = cat_row["DefaultTeamId"]

        # Priority
        priority = weighted_choice(PRIORITIES, behavior["priority_dist"])

        # Reporter (employee from that dept)
        try:
            dept_emps = reporters_by_dept.get_group(dept_code)
            reporter  = dept_emps.sample(1).iloc[0]
        except Exception:
            reporter = emp_df[emp_df["Role"] == "Employee"].sample(1).iloc[0]

        # Assigned agent
        try:
            team_agents = agents_by_team.get_group(team_id)
            agent = team_agents.sample(1).iloc[0]
        except Exception:
            agent = emp_df[emp_df["Role"] == "Agent"].sample(1).iloc[0]

        # Created at
        created_at = random_dt(START_DATE, END_DATE)
        sla_hours_val = sla_hours[priority]
        sla_deadline  = add_hours(created_at, sla_hours_val)

        # Will this issue breach SLA?
        cat_breach_rate = CATEGORY_BEHAVIOR.get(cat_name, {}).get(
            "sla_breach_rate", behavior["sla_breach_rate"]
        )
        will_breach = random.random() < cat_breach_rate

        # Resolution multiplier
        res_mult = CATEGORY_BEHAVIOR.get(cat_name, {}).get(
            "avg_resolution_hours_multiplier", 1.0
        )

        # Will go through Waiting?
        has_waiting = random.random() < behavior["waiting_probability"]

        # Will be cancelled?
        is_cancelled = random.random() < behavior["cancellation_probability"]

        # Final status
        if is_cancelled:
            final_status = "Cancelled"
        elif will_breach:
            # Breached — may or may not be resolved
            if random.random() < 0.6:
                final_status = "Closed"
            else:
                final_status = "In Progress"  # Still open at data generation time
        else:
            r = random.random()
            if r < 0.72:
                final_status = "Closed"
            elif r < 0.83:
                final_status = "Resolved"
            elif r < 0.90:
                final_status = "In Progress"
            else:
                final_status = "Assigned"

        # Compute timestamps
        first_response_at = None
        resolved_at       = None
        closed_at         = None

        if final_status not in ["Cancelled", "New", "Assigned"]:
            # First response
            response_delay_hours = random.uniform(0.1, 2.0)
            if priority == "Critical": response_delay_hours = random.uniform(0.05, 0.5)
            elif priority == "High":   response_delay_hours = random.uniform(0.1, 1.0)
            first_response_at = add_hours(created_at, response_delay_hours)

        if final_status in ["Resolved", "Closed"]:
            # Resolution time
            base_hours = sla_hours_val * res_mult
            if will_breach:
                # Resolved AFTER deadline (breach)
                extra = random.uniform(0.1, sla_hours_val * 0.8)
                resolution_hours = sla_hours_val + extra
            else:
                # Resolved before deadline
                resolution_hours = random.uniform(
                    sla_hours_val * 0.1,
                    sla_hours_val * 0.88
                )

            # Add waiting time
            if has_waiting:
                wait_hours = abs(np.random.normal(
                    behavior["avg_waiting_hours"],
                    behavior["avg_waiting_hours"] * 0.4
                ))
                resolution_hours += wait_hours

            resolved_at = add_hours(created_at, resolution_hours)

            # Ensure resolved_at doesn't exceed END_DATE
            if resolved_at > END_DATE:
                resolved_at = add_hours(created_at, sla_hours_val * 0.5)

            if final_status == "Closed":
                closed_at = add_hours(resolved_at, random.uniform(0.5, 4.0))
                if closed_at > END_DATE:
                    closed_at = add_hours(resolved_at, 0.5)

        # Reopen
        will_reopen = (
            final_status in ["Resolved", "Closed"]
            and random.random() < behavior["reopen_probability"]
        )
        reopen_count = 0
        if will_reopen:
            reopen_count = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            final_status = "Reopened" if random.random() < 0.3 else final_status

        # Root cause (only for resolved issues)
        root_cause_id = None
        if final_status in ["Resolved", "Closed"]:
            rw = ROOT_CAUSE_WEIGHTS.get(cat_name, [1]*10)
            root_cause_id = weighted_choice(root_cause_ids, rw)

        resolution_code_id = None
        resolution_summary = None
        if final_status in ["Resolved", "Closed"]:
            resolution_code_id = random.choice(res_code_ids)
            resolution_summary = f"{cat_name} issue resolved. " + fake.sentence()

        issue_number = f"OPS-2026-{issue_counter:04d}"
        issue_id     = new_id()
        issue_counter += 1

        last_updated = resolved_at or closed_at or first_response_at or created_at

        issues.append({
            "IssueId":           issue_id,
            "IssueNumber":       issue_number,
            "Title":             random.choice(ISSUE_TITLES.get(cat_name, ["Operational issue"])),
            "Description":       fake.paragraph(nb_sentences=3),
            "CreatedBy":         reporter["EmployeeId"],
            "CreatedByName":     reporter["EmployeeName"],
            "CreatedAt":         format_dt(created_at),
            "DepartmentId":      dept_id,
            "DepartmentCode":    dept_code,
            "CategoryId":        cat_id,
            "CategoryName":      cat_name,
            "AssignedTeamId":    team_id,
            "AssignedTeamName":  cat_row["DefaultTeamName"],
            "AssignedAgentId":   agent["EmployeeId"],
            "AssignedAgentName": agent["EmployeeName"],
            "Priority":          priority,
            "Status":            final_status,
            "SLAId":             sla_map[priority],
            "SLATargetHours":    sla_hours_val,
            "SLADeadline":       format_dt(sla_deadline),
            "FirstResponseAt":   format_dt(first_response_at) if first_response_at else "",
            "ResolvedAt":        format_dt(resolved_at) if resolved_at else "",
            "ClosedAt":          format_dt(closed_at) if closed_at else "",
            "RootCauseId":       root_cause_id or "",
            "ResolutionCodeId":  resolution_code_id or "",
            "ResolutionSummary": resolution_summary or "",
            "ReopenCount":       reopen_count,
            "HasWaiting":        has_waiting,        # helper column for history
            "WillBreach":        will_breach,         # helper column for history
            "FirstResponseAt_dt":first_response_at,   # keep as datetime for history gen
            "ResolvedAt_dt":     resolved_at,
            "ClosedAt_dt":       closed_at,
            "CreatedAt_dt":      created_at,
            "LastUpdatedAt":     format_dt(last_updated),
        })

    return pd.DataFrame(issues)

# ── Issue History generation ──────────────────────────────────────────────────

def generate_history(issues_df, emp_df):
    """Generate IssueHistory event log for all issues."""
    history = []
    system_id = "SYSTEM"

    agents_by_team = emp_df[emp_df["Role"] == "Agent"].groupby("TeamId")

    for _, issue in issues_df.iterrows():
        created_at  = issue["CreatedAt_dt"]
        resolved_at = issue["ResolvedAt_dt"]
        closed_at   = issue["ClosedAt_dt"]
        first_resp  = issue["FirstResponseAt_dt"]
        status      = issue["Status"]
        has_waiting = issue["HasWaiting"]
        will_breach = issue["WillBreach"]
        team_id     = issue["AssignedTeamId"]
        agent_id    = issue["AssignedAgentId"]
        issue_id    = issue["IssueId"]
        priority    = issue["Priority"]

        events = []

        # 1 — Created
        events.append({
            "HistoryId":        new_id(),
            "IssueId":          issue_id,
            "EventType":        "Created",
            "PreviousStatus":   "",
            "NewStatus":        "New",
            "PreviousTeam":     "",
            "NewTeam":          issue["AssignedTeamName"],
            "ChangedBy":        issue["CreatedBy"],
            "ChangeTimestamp":  format_dt(created_at),
            "Notes":            "Issue submitted by employee",
        })

        # 2 — Assigned (a few minutes after creation)
        assigned_at = add_hours(created_at, random.uniform(0.05, 0.5))
        events.append({
            "HistoryId":        new_id(),
            "IssueId":          issue_id,
            "EventType":        "Assigned",
            "PreviousStatus":   "New",
            "NewStatus":        "Assigned",
            "PreviousTeam":     "",
            "NewTeam":          issue["AssignedTeamName"],
            "ChangedBy":        system_id,
            "ChangeTimestamp":  format_dt(assigned_at),
            "Notes":            f"Auto-assigned to {issue['AssignedTeamName']} based on category",
        })

        if status in ["Cancelled"]:
            # Only Created + Assigned + Cancel
            cancel_at = add_hours(created_at, random.uniform(0.5, 4.0))
            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "StatusChanged",
                "PreviousStatus":   "Assigned",
                "NewStatus":        "Cancelled",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        issue["CreatedBy"],
                "ChangeTimestamp":  format_dt(cancel_at),
                "Notes":            "Issue cancelled by requester",
            })
            history.extend(events)
            continue

        if status in ["Assigned"]:
            # Never progressed
            history.extend(events)
            continue

        # 3 — In Progress (agent starts)
        if first_resp:
            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "StatusChanged",
                "PreviousStatus":   "Assigned",
                "NewStatus":        "In Progress",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        agent_id,
                "ChangeTimestamp":  format_dt(first_resp),
                "Notes":            "Agent commenced investigation",
            })

        # 4 — Waiting (optional)
        waiting_start = None
        waiting_end   = None
        if has_waiting and first_resp:
            work_before_wait = random.uniform(0.3, 2.0)
            waiting_start = add_hours(first_resp, work_before_wait)
            dept_code = issue["DepartmentCode"]
            avg_wait = DEPT_BEHAVIOR[dept_code]["avg_waiting_hours"]
            wait_duration = abs(np.random.normal(avg_wait, avg_wait * 0.3))
            waiting_end = add_hours(waiting_start, wait_duration)

            if resolved_at and waiting_end >= resolved_at:
                waiting_end = add_hours(waiting_start, wait_duration * 0.3)

            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "StatusChanged",
                "PreviousStatus":   "In Progress",
                "NewStatus":        "Waiting",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        agent_id,
                "ChangeTimestamp":  format_dt(waiting_start),
                "Notes":            random.choice([
                    "Waiting for manager approval",
                    "Waiting for supplier response",
                    "Pending additional information from requester",
                    "Awaiting finance sign-off",
                    "Waiting for third-party vendor",
                ]),
            })

            # Return from Waiting
            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "StatusChanged",
                "PreviousStatus":   "Waiting",
                "NewStatus":        "In Progress",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        agent_id,
                "ChangeTimestamp":  format_dt(waiting_end),
                "Notes":            "Resumed — required information received",
            })

        # 5 — Transfer (occasional)
        dept_code = issue["DepartmentCode"]
        if random.random() < DEPT_BEHAVIOR[dept_code]["transfer_probability"]:
            transfer_time = add_hours(first_resp or assigned_at, random.uniform(1.0, 4.0))
            if resolved_at and transfer_time >= resolved_at:
                pass  # skip transfer if already resolved
            else:
                events.append({
                    "HistoryId":        new_id(),
                    "IssueId":          issue_id,
                    "EventType":        "Transferred",
                    "PreviousStatus":   "In Progress",
                    "NewStatus":        "In Progress",
                    "PreviousTeam":     issue["AssignedTeamName"],
                    "NewTeam":          issue["AssignedTeamName"] + " (transferred)",
                    "ChangedBy":        agent_id,
                    "ChangeTimestamp":  format_dt(transfer_time),
                    "Notes":            "Issue transferred to specialist team",
                })

        # 6 — Resolved
        if resolved_at and status in ["Resolved", "Closed", "Reopened"]:
            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "Resolved",
                "PreviousStatus":   "In Progress",
                "NewStatus":        "Resolved",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        agent_id,
                "ChangeTimestamp":  format_dt(resolved_at),
                "Notes":            "Issue resolved. " + (issue["ResolutionSummary"][:80] if issue["ResolutionSummary"] else ""),
            })

        # 7 — Closed
        if closed_at and status == "Closed":
            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "Closed",
                "PreviousStatus":   "Resolved",
                "NewStatus":        "Closed",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        issue["CreatedBy"],
                "ChangeTimestamp":  format_dt(closed_at),
                "Notes":            "Issue confirmed closed by requester",
            })

        # 8 — Reopen (if applicable)
        if issue["ReopenCount"] > 0 and resolved_at:
            reopen_at = add_hours(resolved_at, random.uniform(2.0, 24.0))
            events.append({
                "HistoryId":        new_id(),
                "IssueId":          issue_id,
                "EventType":        "Reopened",
                "PreviousStatus":   "Resolved",
                "NewStatus":        "Reopened",
                "PreviousTeam":     issue["AssignedTeamName"],
                "NewTeam":          issue["AssignedTeamName"],
                "ChangedBy":        issue["CreatedBy"],
                "ChangeTimestamp":  format_dt(reopen_at),
                "Notes":            "Issue reopened — resolution not satisfactory",
            })

        history.extend(events)

    return pd.DataFrame(history)

# ── Comments generation ───────────────────────────────────────────────────────

COMMENT_TEMPLATES = [
    "Investigating the issue — will update shortly.",
    "Confirmed the problem. Working on a fix now.",
    "Issue reproduced. Root cause identified as {rc}.",
    "Waiting for manager approval before proceeding.",
    "Contacted the supplier regarding this. Awaiting response.",
    "Applied the fix. Please test and confirm resolution.",
    "This appears to be a recurring issue — will escalate.",
    "Update: issue is more complex than initially assessed.",
    "Checked with the finance team — approval is pending.",
    "Resolution applied. Monitoring for 24 hours.",
]

def generate_comments(issues_df, emp_df):
    """Generate realistic comments for issues."""
    comments = []
    agents = emp_df[emp_df["Role"] == "Agent"]

    for _, issue in issues_df.iterrows():
        status = issue["Status"]
        if status in ["Cancelled", "Assigned", "New"]:
            continue

        n_comments = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
        created_at = issue["CreatedAt_dt"]
        resolved_at = issue["ResolvedAt_dt"]
        # Guard against NaN (pandas may return float NaN for missing datetimes)
        if resolved_at is None or (not isinstance(resolved_at, datetime) and pd.isna(resolved_at)):
            resolved_at = add_hours(created_at, 8)

        end_time = add_hours(created_at, 48)
        if isinstance(resolved_at, datetime):
            end_time = min(resolved_at, end_time)

        for i in range(n_comments):
            comment_time = random_dt(
                add_hours(created_at, 0.2),
                end_time
            )
            author = agents.sample(1).iloc[0]
            is_internal = random.random() < 0.25

            template = random.choice(COMMENT_TEMPLATES)
            comment_text = template.replace("{rc}", issue["CategoryName"].lower())

            comments.append({
                "CommentId":     new_id(),
                "IssueId":       issue["IssueId"],
                "CommentText":   comment_text,
                "CommentAuthor": author["EmployeeId"],
                "AuthorName":    author["EmployeeName"],
                "CreatedAt":     format_dt(comment_time),
                "IsInternal":    is_internal,
            })

    return pd.DataFrame(comments)

# ── Escalations generation ────────────────────────────────────────────────────

def generate_escalations(issues_df, emp_df):
    """Generate escalation records for breached/critical issues."""
    escalations = []
    managers = emp_df[emp_df["Role"] == "Manager"]

    for _, issue in issues_df.iterrows():
        if not issue["WillBreach"]:
            continue
        if issue["Status"] in ["Cancelled", "New"]:
            continue

        manager = managers.sample(1).iloc[0]
        created_at = issue["CreatedAt_dt"]
        sla_hours_val = issue["SLATargetHours"]
        escalation_at = add_hours(created_at, sla_hours_val * 1.05)

        resolved_at = issue["ResolvedAt_dt"]
        esc_resolved = add_hours(escalation_at, random.uniform(1.0, 6.0)) if resolved_at else None

        escalations.append({
            "EscalationId":    new_id(),
            "IssueId":         issue["IssueId"],
            "IssueNumber":     issue["IssueNumber"],
            "EscalationLevel": 1,
            "EscalatedTo":     manager["EmployeeId"],
            "EscalatedToName": manager["EmployeeName"],
            "Reason":          f"SLA Deadline exceeded for {issue['Priority']} priority issue",
            "EscalatedAt":     format_dt(escalation_at),
            "ResolvedAt":      format_dt(esc_resolved) if esc_resolved else "",
        })

    return pd.DataFrame(escalations)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("OpsInsight Synthetic Data Generator")
    print("Northstar Operations Group")
    print("=" * 60)

    print("\n[1/9] Generating departments...")
    dept_df = build_departments()
    print(f"      {len(dept_df)} departments")

    print("[2/9] Generating teams...")
    team_df = build_teams(dept_df)
    print(f"      {len(team_df)} teams")

    print("[3/9] Generating categories...")
    cat_df = build_categories(dept_df, team_df)
    print(f"      {len(cat_df)} categories")

    print("[4/9] Generating SLA rules...")
    sla_df = build_sla_rules()
    print(f"      {len(sla_df)} SLA rules")

    print("[5/9] Generating root causes and resolution codes...")
    rc_df  = build_root_causes()
    res_df = build_resolution_codes()
    print(f"      {len(rc_df)} root causes, {len(res_df)} resolution codes")

    print("[6/9] Generating employees...")
    emp_df = build_employees(dept_df, team_df)
    print(f"      {len(emp_df)} employees")

    print("[7/9] Generating issues...")
    issues_df = generate_issues(dept_df, team_df, cat_df, sla_df, emp_df, rc_df, res_df)
    print(f"      {len(issues_df)} issues generated")

    print("[8/9] Generating issue history...")
    history_df = generate_history(issues_df, emp_df)
    print(f"      {len(history_df)} history events")

    print("[8b]  Generating comments...")
    comments_df = generate_comments(issues_df, emp_df)
    print(f"      {len(comments_df)} comments")

    print("[9/9] Generating escalations...")
    esc_df = generate_escalations(issues_df, emp_df)
    print(f"      {len(esc_df)} escalations")

    # ── Drop helper columns before export ──────────────────────────────────
    export_cols_issues = [
        "IssueId", "IssueNumber", "Title", "Description",
        "CreatedBy", "CreatedByName", "CreatedAt", "DepartmentId", "DepartmentCode",
        "CategoryId", "CategoryName", "AssignedTeamId", "AssignedTeamName",
        "AssignedAgentId", "AssignedAgentName", "Priority", "Status",
        "SLAId", "SLATargetHours", "SLADeadline",
        "FirstResponseAt", "ResolvedAt", "ClosedAt",
        "RootCauseId", "ResolutionCodeId", "ResolutionSummary",
        "ReopenCount", "LastUpdatedAt",
    ]

    # ── Write CSVs ──────────────────────────────────────────────────────────
    print("\nWriting CSV files...")

    dept_df.to_csv(f"{OUTPUT_DIR}/departments.csv", index=False)
    team_df.drop(columns=["DepartmentCode"], errors="ignore").to_csv(
        f"{OUTPUT_DIR}/teams.csv", index=False)
    cat_df.to_csv(f"{OUTPUT_DIR}/categories.csv", index=False)
    sla_df.to_csv(f"{OUTPUT_DIR}/sla_rules.csv", index=False)
    rc_df.to_csv(f"{OUTPUT_DIR}/root_causes.csv", index=False)
    res_df.to_csv(f"{OUTPUT_DIR}/resolution_codes.csv", index=False)
    emp_df.to_csv(f"{OUTPUT_DIR}/employees.csv", index=False)
    issues_df[export_cols_issues].to_csv(f"{OUTPUT_DIR}/issues.csv", index=False)
    history_df.to_csv(f"{OUTPUT_DIR}/issue_history.csv", index=False)
    comments_df.to_csv(f"{OUTPUT_DIR}/comments.csv", index=False)
    esc_df.to_csv(f"{OUTPUT_DIR}/escalations.csv", index=False)

    # ── Summary stats ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nFiles written to: {OUTPUT_DIR}/")
    print(f"\nIssue Summary:")
    print(issues_df["Status"].value_counts().to_string())
    print(f"\nPriority Distribution:")
    print(issues_df["Priority"].value_counts().to_string())
    print(f"\nDepartment Distribution:")
    print(issues_df["DepartmentCode"].value_counts().to_string())

    resolved = issues_df[issues_df["Status"].isin(["Resolved", "Closed"])]
    breached = issues_df[issues_df["WillBreach"] == True]
    print(f"\nSLA Statistics:")
    print(f"  Resolved/Closed: {len(resolved)} ({len(resolved)/len(issues_df)*100:.1f}%)")
    print(f"  SLA Breached:    {len(breached)} ({len(breached)/len(issues_df)*100:.1f}%)")
    if len(resolved) > 0:
        compliance = (len(resolved) - len(issues_df[(issues_df['WillBreach']) & (issues_df['Status'].isin(['Resolved','Closed']))])) / len(resolved) * 100
        print(f"  SLA Compliance:  {compliance:.1f}%")

    print(f"\nHistory Events by Type:")
    print(history_df["EventType"].value_counts().to_string())

if __name__ == "__main__":
    main()
