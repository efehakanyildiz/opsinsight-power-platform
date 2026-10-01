-- =============================================================================
-- OpsInsight — Operational Queries
-- =============================================================================
-- Standard operational reporting queries
-- Run against: PostgreSQL with OpsInsight schema
-- =============================================================================

-- ── Q1: Current Open Issues Summary ──────────────────────────────────────────
-- Provides a count of open issues grouped by priority and department

SELECT
    d.department_name,
    i.priority,
    COUNT(*)                                AS open_issues,
    COUNT(*) FILTER (WHERE i.sla_status = 'Warning')   AS sla_warning,
    COUNT(*) FILTER (WHERE i.sla_status = 'Critical')  AS sla_critical,
    COUNT(*) FILTER (WHERE i.sla_status = 'Breached')  AS sla_breached
FROM issues i
JOIN departments d ON d.department_id = i.department_id
WHERE i.status NOT IN ('Resolved', 'Closed', 'Cancelled')
GROUP BY d.department_name, i.priority
ORDER BY
    d.department_name,
    CASE i.priority
        WHEN 'Critical' THEN 1
        WHEN 'High'     THEN 2
        WHEN 'Medium'   THEN 3
        ELSE 4
    END;

-- ── Q2: Issues by Department and Category ────────────────────────────────────
-- Volume breakdown for understanding issue distribution

SELECT
    d.department_name,
    c.category_name,
    COUNT(*)                        AS total_issues,
    COUNT(*) FILTER (WHERE i.status NOT IN ('Resolved', 'Closed', 'Cancelled'))
                                    AS open_issues,
    COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                    AS resolved_issues,
    ROUND(
        COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 1
    )                               AS resolution_rate_pct
FROM issues i
JOIN departments d    ON d.department_id = i.department_id
JOIN issue_categories c ON c.category_id = i.category_id
GROUP BY d.department_name, c.category_name
ORDER BY d.department_name, total_issues DESC;

-- ── Q3: Team Workload Dashboard ───────────────────────────────────────────────
-- Operations manager view of current team workloads

SELECT
    t.team_name,
    d.department_name,
    COUNT(*)                        AS total_open,
    COUNT(*) FILTER (WHERE i.priority = 'Critical')  AS critical,
    COUNT(*) FILTER (WHERE i.priority = 'High')      AS high,
    COUNT(*) FILTER (WHERE i.priority = 'Medium')    AS medium,
    COUNT(*) FILTER (WHERE i.priority = 'Low')       AS low,
    COUNT(*) FILTER (WHERE i.sla_status = 'Breached') AS breached,
    COUNT(*) FILTER (WHERE i.sla_status = 'Critical') AS sla_critical,
    COUNT(*) FILTER (WHERE i.sla_status = 'Warning')  AS sla_warning
FROM issues i
JOIN teams t        ON t.team_id = i.assigned_team_id
JOIN departments d  ON d.department_id = t.department_id
WHERE i.status NOT IN ('Resolved', 'Closed', 'Cancelled')
GROUP BY t.team_name, d.department_name
ORDER BY critical DESC, breached DESC, high DESC;

-- ── Q4: Issue Aging Report ────────────────────────────────────────────────────
-- Identifies long-running unresolved issues

SELECT
    i.issue_number,
    i.title,
    d.department_name,
    c.category_name,
    i.priority,
    i.status,
    t.team_name                     AS assigned_team,
    e.employee_name                 AS assigned_agent,
    i.created_at,
    EXTRACT(EPOCH FROM (NOW() - i.created_at)) / 3600
                                    AS age_hours,
    i.sla_deadline,
    i.sla_status
FROM issues i
JOIN departments d    ON d.department_id = i.department_id
JOIN issue_categories c ON c.category_id = i.category_id
LEFT JOIN teams t     ON t.team_id = i.assigned_team_id
LEFT JOIN employees e ON e.employee_id = i.assigned_agent_id
WHERE i.status NOT IN ('Resolved', 'Closed', 'Cancelled')
ORDER BY age_hours DESC
LIMIT 50;

-- ── Q5: Recently Resolved Issues ─────────────────────────────────────────────
-- Shows resolution activity for last 7 days

SELECT
    i.issue_number,
    i.title,
    d.department_name,
    c.category_name,
    i.priority,
    e_agent.employee_name           AS resolved_by,
    i.created_at,
    i.resolved_at,
    ROUND(
        EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)) / 3600, 1
    )                               AS resolution_hours,
    rc.root_cause_name,
    res.resolution_name
FROM issues i
JOIN departments d       ON d.department_id = i.department_id
JOIN issue_categories c  ON c.category_id = i.category_id
LEFT JOIN employees e_agent ON e_agent.employee_id = i.assigned_agent_id
LEFT JOIN root_causes rc     ON rc.root_cause_id = i.root_cause_id
LEFT JOIN resolution_codes res ON res.resolution_code_id = i.resolution_code_id
WHERE i.status IN ('Resolved', 'Closed')
  AND i.resolved_at >= NOW() - INTERVAL '7 days'
ORDER BY i.resolved_at DESC;

-- ── Q6: Reopened Issues Analysis ─────────────────────────────────────────────
-- Issues that have been reopened — quality signal

SELECT
    i.issue_number,
    i.title,
    d.department_name,
    c.category_name,
    i.priority,
    i.status,
    i.reopen_count,
    rc.root_cause_name,
    res.resolution_name,
    e_agent.employee_name           AS assigned_agent
FROM issues i
JOIN departments d       ON d.department_id = i.department_id
JOIN issue_categories c  ON c.category_id = i.category_id
LEFT JOIN employees e_agent ON e_agent.employee_id = i.assigned_agent_id
LEFT JOIN root_causes rc     ON rc.root_cause_id = i.root_cause_id
LEFT JOIN resolution_codes res ON res.resolution_code_id = i.resolution_code_id
WHERE i.reopen_count > 0
ORDER BY i.reopen_count DESC, i.created_at DESC;

-- ── Q7: Monthly Issue Volume Trend ───────────────────────────────────────────
-- Tracks whether operational demand is growing or shrinking

SELECT
    DATE_TRUNC('month', i.created_at)  AS month,
    COUNT(*)                            AS total_created,
    COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                        AS total_resolved,
    COUNT(*) FILTER (WHERE i.priority = 'Critical') AS critical_created,
    COUNT(*) FILTER (WHERE i.priority = 'High')     AS high_created
FROM issues i
GROUP BY DATE_TRUNC('month', i.created_at)
ORDER BY month;
