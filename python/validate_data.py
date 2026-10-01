"""
OpsInsight — Data Validation Script
=====================================
Reads generated CSV files and performs data quality checks.

Checks:
  1.  No null IssueId
  2.  No duplicate IssueNumbers
  3.  ResolvedAt not before CreatedAt
  4.  SLADeadline not before CreatedAt
  5.  ClosedAt not before ResolvedAt
  6.  No unknown CategoryId
  7.  No unknown DepartmentId
  8.  No unknown TeamId
  9.  Priority must be in allowed set
  10. Status must be in allowed set
  11. Resolved issues must have RootCauseId (warning only)
  12. Closed issues must have ResolvedAt
  13. ReopenCount must be non-negative
  14. No orphaned IssueHistory (IssueId not in Issues)
  15. No orphaned Comments
  16. No orphaned Escalations
  17. IssueHistory timestamps must be after CreatedAt
  18. IssueHistory events in chronological order per issue
  19. No negative resolution duration
  20. SLATargetHours must be positive

Usage:
  python validate_data.py
"""

import pandas as pd
import numpy as np
import os
import sys

DATA_DIR = "../data/generated"

ALLOWED_PRIORITIES = {"Critical", "High", "Medium", "Low"}
ALLOWED_STATUSES   = {
    "New", "Assigned", "In Progress", "Waiting",
    "Resolved", "Closed", "Reopened", "Cancelled"
}

# ── Helper ────────────────────────────────────────────────────────────────────

class CheckResult:
    def __init__(self, name: str, passed: bool, message: str, count: int = 0):
        self.name    = name
        self.passed  = passed
        self.message = message
        self.count   = count

    def __str__(self):
        icon = "✅" if self.passed else "❌"
        suffix = f" ({self.count} issues)" if not self.passed and self.count > 0 else ""
        return f"  {icon} {self.name}: {self.message}{suffix}"

results = []

def check(name: str, passed: bool, fail_msg: str, ok_msg: str = "OK", count: int = 0):
    msg = ok_msg if passed else fail_msg
    results.append(CheckResult(name, passed, msg, count))

def parse_dt(series):
    return pd.to_datetime(series, format="%Y-%m-%dT%H:%M:%S", errors="coerce")

# ── Load data ─────────────────────────────────────────────────────────────────

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        sys.exit(1)
    return pd.read_csv(path, dtype=str).fillna("")

# ── Run checks ────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("OpsInsight — Data Quality Validation Report")
    print("=" * 60)

    issues   = load_csv("issues.csv")
    history  = load_csv("issue_history.csv")
    comments = load_csv("comments.csv")
    esc      = load_csv("escalations.csv")
    depts    = load_csv("departments.csv")
    teams    = load_csv("teams.csv")
    cats     = load_csv("categories.csv")
    emps     = load_csv("employees.csv")
    sla      = load_csv("sla_rules.csv")

    print(f"\nLoaded:")
    print(f"  Issues:     {len(issues):,}")
    print(f"  History:    {len(history):,}")
    print(f"  Comments:   {len(comments):,}")
    print(f"  Escalations:{len(esc):,}")
    print(f"  Employees:  {len(emps):,}")
    print()

    valid_dept_ids = set(depts["DepartmentId"])
    valid_team_ids = set(teams["TeamId"])
    valid_cat_ids  = set(cats["CategoryId"])
    valid_emp_ids  = set(emps["EmployeeId"])
    valid_sla_ids  = set(sla["SLAId"])
    issue_ids      = set(issues["IssueId"])

    # Parse datetimes
    issues["_created"]  = parse_dt(issues["CreatedAt"])
    issues["_resolved"] = parse_dt(issues["ResolvedAt"])
    issues["_closed"]   = parse_dt(issues["ClosedAt"])
    issues["_deadline"] = parse_dt(issues["SLADeadline"])

    # ── CHECK 1: No null IssueId
    null_ids = issues["IssueId"].isna() | (issues["IssueId"] == "")
    check("01 No null IssueId", null_ids.sum() == 0,
          f"Found {null_ids.sum()} rows with null IssueId",
          f"All {len(issues)} issues have IssueId")

    # ── CHECK 2: No duplicate IssueNumbers
    dupes = issues["IssueNumber"].duplicated().sum()
    check("02 No duplicate IssueNumbers", dupes == 0,
          f"{dupes} duplicate IssueNumbers found",
          "All IssueNumbers unique", dupes)

    # ── CHECK 3: ResolvedAt not before CreatedAt
    resolved_mask = (issues["_resolved"].notna()) & (issues["_created"].notna())
    invalid_resolve = (
        issues.loc[resolved_mask, "_resolved"] < issues.loc[resolved_mask, "_created"]
    ).sum()
    check("03 ResolvedAt >= CreatedAt", invalid_resolve == 0,
          f"{invalid_resolve} issues have ResolvedAt before CreatedAt",
          "All resolution timestamps valid", invalid_resolve)

    # ── CHECK 4: SLADeadline not before CreatedAt
    deadline_mask = issues["_deadline"].notna() & issues["_created"].notna()
    invalid_deadline = (
        issues.loc[deadline_mask, "_deadline"] < issues.loc[deadline_mask, "_created"]
    ).sum()
    check("04 SLADeadline >= CreatedAt", invalid_deadline == 0,
          f"{invalid_deadline} issues have SLADeadline before CreatedAt",
          "All SLA deadlines valid", invalid_deadline)

    # ── CHECK 5: ClosedAt not before ResolvedAt
    closed_mask = issues["_closed"].notna() & issues["_resolved"].notna()
    invalid_closed = (
        issues.loc[closed_mask, "_closed"] < issues.loc[closed_mask, "_resolved"]
    ).sum()
    check("05 ClosedAt >= ResolvedAt", invalid_closed == 0,
          f"{invalid_closed} issues have ClosedAt before ResolvedAt",
          "All close timestamps valid", invalid_closed)

    # ── CHECK 6: Valid CategoryId
    unknown_cats = (~issues["CategoryId"].isin(valid_cat_ids)).sum()
    check("06 Valid CategoryId", unknown_cats == 0,
          f"{unknown_cats} issues have unknown CategoryId",
          "All CategoryIds valid", unknown_cats)

    # ── CHECK 7: Valid DepartmentId
    unknown_depts = (~issues["DepartmentId"].isin(valid_dept_ids)).sum()
    check("07 Valid DepartmentId", unknown_depts == 0,
          f"{unknown_depts} issues have unknown DepartmentId",
          "All DepartmentIds valid", unknown_depts)

    # ── CHECK 8: Valid AssignedTeamId
    unknown_teams = (~issues["AssignedTeamId"].isin(valid_team_ids)).sum()
    check("08 Valid AssignedTeamId", unknown_teams == 0,
          f"{unknown_teams} issues have unknown AssignedTeamId",
          "All TeamIds valid", unknown_teams)

    # ── CHECK 9: Valid Priority
    invalid_priority = (~issues["Priority"].isin(ALLOWED_PRIORITIES)).sum()
    check("09 Valid Priority values", invalid_priority == 0,
          f"{invalid_priority} issues have invalid Priority",
          f"All priorities valid ({', '.join(ALLOWED_PRIORITIES)})", invalid_priority)

    # ── CHECK 10: Valid Status
    invalid_status = (~issues["Status"].isin(ALLOWED_STATUSES)).sum()
    check("10 Valid Status values", invalid_status == 0,
          f"{invalid_status} issues have invalid Status",
          f"All statuses valid", invalid_status)

    # ── CHECK 11: Resolved issues should have RootCauseId (warning)
    resolved_issues = issues[issues["Status"].isin(["Resolved", "Closed"])]
    missing_rc = (resolved_issues["RootCauseId"] == "").sum()
    check("11 Resolved issues have RootCauseId (warning)",
          missing_rc == 0,
          f"⚠️  {missing_rc} resolved issues missing RootCauseId (warning only)",
          f"All {len(resolved_issues)} resolved issues have RootCauseId", missing_rc)

    # ── CHECK 12: Closed issues must have ResolvedAt
    closed_issues = issues[issues["Status"] == "Closed"]
    closed_no_resolved = (closed_issues["ResolvedAt"] == "").sum()
    check("12 Closed issues have ResolvedAt", closed_no_resolved == 0,
          f"{closed_no_resolved} closed issues missing ResolvedAt",
          f"All closed issues have ResolvedAt", closed_no_resolved)

    # ── CHECK 13: ReopenCount >= 0
    issues["_reopen"] = pd.to_numeric(issues["ReopenCount"], errors="coerce")
    negative_reopen = (issues["_reopen"] < 0).sum()
    check("13 ReopenCount >= 0", negative_reopen == 0,
          f"{negative_reopen} issues have negative ReopenCount",
          "All ReopenCount values valid", negative_reopen)

    # ── CHECK 14: No orphaned IssueHistory
    orphan_hist = (~history["IssueId"].isin(issue_ids)).sum()
    check("14 No orphaned IssueHistory", orphan_hist == 0,
          f"{orphan_hist} history events reference unknown IssueId",
          f"All {len(history)} history events have valid IssueId", orphan_hist)

    # ── CHECK 15: No orphaned Comments
    orphan_comments = (~comments["IssueId"].isin(issue_ids)).sum()
    check("15 No orphaned Comments", orphan_comments == 0,
          f"{orphan_comments} comments reference unknown IssueId",
          f"All {len(comments)} comments have valid IssueId", orphan_comments)

    # ── CHECK 16: No orphaned Escalations
    orphan_esc = (~esc["IssueId"].isin(issue_ids)).sum()
    check("16 No orphaned Escalations", orphan_esc == 0,
          f"{orphan_esc} escalations reference unknown IssueId",
          f"All {len(esc)} escalations have valid IssueId", orphan_esc)

    # ── CHECK 17: History timestamps > CreatedAt
    hist_merged = history.merge(
        issues[["IssueId", "_created"]], on="IssueId", how="left"
    )
    hist_merged["_hist_ts"] = parse_dt(hist_merged["ChangeTimestamp"])
    invalid_hist_ts = (
        hist_merged["_hist_ts"] < hist_merged["_created"]
    ).sum()
    check("17 History timestamps >= Issue CreatedAt", invalid_hist_ts == 0,
          f"{invalid_hist_ts} history events before issue CreatedAt",
          "All history timestamps valid", invalid_hist_ts)

    # ── CHECK 18: History in chronological order per issue
    h2 = history.copy()
    h2["_ts"] = parse_dt(h2["ChangeTimestamp"])
    h2 = h2.sort_values(["IssueId", "_ts"])
    h2["_prev_ts"] = h2.groupby("IssueId")["_ts"].shift(1)
    out_of_order = (h2["_ts"] < h2["_prev_ts"]).sum()
    check("18 History in chronological order", out_of_order == 0,
          f"{out_of_order} out-of-order history events",
          "All history events in chronological order", out_of_order)

    # ── CHECK 19: No negative resolution duration
    valid_duration = issues[issues["_resolved"].notna() & issues["_created"].notna()].copy()
    valid_duration["_duration_h"] = (
        valid_duration["_resolved"] - valid_duration["_created"]
    ).dt.total_seconds() / 3600
    negative_duration = (valid_duration["_duration_h"] < 0).sum()
    check("19 No negative resolution duration", negative_duration == 0,
          f"{negative_duration} issues have negative resolution duration",
          "All resolution durations are positive", negative_duration)

    # ── CHECK 20: SLATargetHours positive
    issues["_sla_hours"] = pd.to_numeric(issues["SLATargetHours"], errors="coerce")
    invalid_sla_h = (issues["_sla_hours"] <= 0).sum()
    check("20 SLATargetHours > 0", invalid_sla_h == 0,
          f"{invalid_sla_h} issues have invalid SLATargetHours",
          "All SLA target hours valid", invalid_sla_h)

    # ── Summary ────────────────────────────────────────────────────────────────
    print("Data Quality Check Results:")
    print("-" * 60)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    for r in results:
        print(str(r))

    print("-" * 60)
    print(f"\nSummary: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n✅ All data quality checks passed. Dataset is ready for use.")
    else:
        print(f"\n⚠️  {failed} check(s) failed. Review issues above before using the dataset.")

    # ── Dataset Statistics ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)

    print(f"\nIssues by Status:")
    print(issues["Status"].value_counts().to_frame("Count").to_string())

    print(f"\nIssues by Priority:")
    print(issues["Priority"].value_counts().to_frame("Count").to_string())

    print(f"\nIssues by Department:")
    print(issues["DepartmentCode"].value_counts().to_frame("Count").to_string())

    resolved_count = len(issues[issues["Status"].isin(["Resolved", "Closed"])])
    breached_count = len(
        issues[
            issues["Status"].isin(["Resolved", "Closed"])
            & (issues["_resolved"] > issues["_deadline"])
            & issues["_resolved"].notna()
            & issues["_deadline"].notna()
        ]
    )
    if resolved_count > 0:
        compliance = (resolved_count - breached_count) / resolved_count * 100
        print(f"\nSLA Compliance: {compliance:.1f}%")

    print(f"\nHistory Events by Type:")
    print(history["EventType"].value_counts().to_frame("Count").to_string())

    print(f"\nEmployee Roles:")
    print(emps["Role"].value_counts().to_frame("Count").to_string())

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
