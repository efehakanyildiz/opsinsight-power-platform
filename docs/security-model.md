# OpsInsight — Security Model

**Version:** 1.0

---

## 1. Security Principles

OpsInsight follows **least privilege** access control.

Each user sees only the data their role requires. No role has unnecessary access.

The design goal:
- Employee: personal transparency without broader exposure
- Agent: team efficiency without cross-team visibility
- Manager: departmental control with strategic insight
- Admin: full configuration without operational interference

---

## 2. Role Definitions

| Role | Access Level | Who Uses It |
|------|-------------|-------------|
| Employee | Own issues only | All staff submitting issues |
| Operations Agent | Team queue | Dedicated issue handlers |
| Team Manager | Department + analytics | Team leads |
| System Admin | Full configuration | IT Admin |

---

## 3. Data Access Matrix

| Data Object | Employee | Agent | Manager | Admin |
|------------|----------|-------|---------|-------|
| Own issues (create/read) | ✅ | ✅ | ✅ | ✅ |
| All team issues | ❌ | ✅ | ✅ | ✅ |
| All department issues | ❌ | ❌ | ✅ | ✅ |
| All issues (all depts) | ❌ | ❌ | ❌ | ✅ |
| Issue comments (external) | ✅ | ✅ | ✅ | ✅ |
| Issue comments (internal) | ❌ | ✅ | ✅ | ✅ |
| SLA Monitor | ❌ | ❌ | ✅ | ✅ |
| Process Insights | ❌ | ❌ | ✅ | ✅ |
| Team Queue | ❌ | ✅ | ✅ | ✅ |
| Administration screens | ❌ | ❌ | ❌ | ✅ |
| SLA rule configuration | ❌ | ❌ | ❌ | ✅ |
| User management | ❌ | ❌ | ❌ | ✅ |

---

## 4. Dataverse Security Implementation

### Table Permissions

| Table | Employee | Agent | Manager | Admin |
|-------|----------|-------|---------|-------|
| Issues | Create, Read (own) | Read (team), Update | Read (dept), Update | Full |
| IssueHistory | Read (own issues) | Read (team issues) | Read (dept) | Full |
| IssueComments | Create, Read (own) | Create, Read (team) | Full (dept) | Full |
| Escalations | Read (own) | Read (team) | Read (dept) | Full |
| Departments | Read | Read | Read | Full |
| Teams | Read | Read | Read | Full |
| Employees | Read (self) | Read (team) | Read (dept) | Full |
| IssueCategories | Read | Read | Read | Full |
| SLARules | Read | Read | Read | Full |
| RootCauses | Read | Read | Read | Full |
| ResolutionCodes | Read | Read | Read | Full |

### Row-Level Security (Dataverse Column Security)

**Issues table RLS logic:**

```
Employee:  CreatedBy = current user ID
Agent:     AssignedTeamId = user's TeamId
Manager:   DepartmentId = user's DepartmentId
Admin:     No filter (full access)
```

### Dataverse Security Roles to Create

1. `OpsInsight Employee` — Basic read/create on Issues
2. `OpsInsight Agent` — Team-scoped read/write on Issues + History
3. `OpsInsight Manager` — Department-scoped read on all tables + write on Issues
4. `OpsInsight Admin` — Full read/write on all tables

---

## 5. Power Apps Security

Role detection in Power Apps:

```powerapps
// OnStart: detect user role
Set(
    currentUserRole,
    LookUp(Employees, Email = User().Email).Role
);

// Navigation visibility
Visible: If(currentUserRole = "Admin", true, false)
```

Navigation items are hidden/shown per role using `Visible` property.

No server-side enforcement is applied purely via canvas app — Dataverse security roles provide the actual enforcement layer.

---

## 6. Power BI Security

### Row-Level Security (RLS) in Power BI

Define RLS roles in Power BI Desktop:

**Manager role:**
```dax
[CreatedByDeptId] = LOOKUPVALUE(
    Employees[DepartmentId],
    Employees[Email], USERPRINCIPALNAME()
)
```

**Agent role:**
```dax
[AssignedTeamId] = LOOKUPVALUE(
    Employees[TeamId],
    Employees[Email], USERPRINCIPALNAME()
)
```

*Note: For portfolio/dev environment, RLS may be applied in simplified form. Full Power BI RLS requires Pro license or Premium capacity for multi-user enforcement.*

---

## 7. Sensitivity Levels

| Data | Sensitivity | Notes |
|------|-------------|-------|
| Employee names | Medium | Synthetic data only in dev |
| Issue descriptions | Medium | May contain operational details |
| Internal comments | High | Not visible to employees |
| Escalation records | High | Manager-only |
| SLA configuration | Medium | Admin-only modification |
| Resolution summaries | Low | Shared with requester |

---

## 8. Audit Trail

The IssueHistory table provides a complete audit trail of:

- Who changed what
- When it changed
- What the value was before and after
- Which team handled it at each stage

This satisfies typical operational audit requirements without additional tooling.

---

## 9. Development Environment Notes

In the Power Apps Developer Plan environment:

- All users share the same Dataverse environment
- Full Dataverse security role implementation is possible
- Power BI row-level security requires individual user sign-in to enforce
- For portfolio demonstration, document the intended security model even where not all constraints are deployable in the single-developer environment
