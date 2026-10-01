-- =============================================================================
-- OpsInsight — SLA Analysis Queries
-- =============================================================================

-- ── Q1: SLA Compliance by Department ─────────────────────────────────────────

SELECT
    d.department_name,
    COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                            AS resolved_total,
    COUNT(*) FILTER (
        WHERE i.status IN ('Resolved', 'Closed')
          AND i.resolved_at <= i.sla_deadline
    )                                       AS resolved_within_sla,
    ROUND(
        COUNT(*) FILTER (
            WHERE i.status IN ('Resolved', 'Closed')
              AND i.resolved_at <= i.sla_deadline
        )::NUMERIC
        / NULLIF(
            COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed')), 0
        ) * 100, 1
    )                                       AS sla_compliance_pct,
    COUNT(*) FILTER (
        WHERE i.status IN ('Resolved', 'Closed')
          AND i.resolved_at > i.sla_deadline
    )                                       AS breached_count
FROM issues i
JOIN departments d ON d.department_id = i.department_id
GROUP BY d.department_name
ORDER BY sla_compliance_pct ASC;

-- ── Q2: SLA Compliance by Category ───────────────────────────────────────────

SELECT
    c.category_name,
    d.department_name,
    COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                            AS resolved_total,
    ROUND(
        COUNT(*) FILTER (
            WHERE i.status IN ('Resolved', 'Closed')
              AND i.resolved_at <= i.sla_deadline
        )::NUMERIC
        / NULLIF(
            COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed')), 0
        ) * 100, 1
    )                                       AS sla_compliance_pct,
    ROUND(
        AVG(
            CASE WHEN i.status IN ('Resolved', 'Closed') AND i.resolved_at IS NOT NULL
            THEN EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)) / 3600
            END
        ), 1
    )                                       AS avg_resolution_hours
FROM issues i
JOIN issue_categories c ON c.category_id = i.category_id
JOIN departments d       ON d.department_id = i.department_id
GROUP BY c.category_name, d.department_name
ORDER BY sla_compliance_pct ASC;

-- ── Q3: SLA Compliance by Priority ───────────────────────────────────────────

SELECT
    i.priority,
    s.target_hours,
    COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                            AS resolved_total,
    ROUND(
        COUNT(*) FILTER (
            WHERE i.status IN ('Resolved', 'Closed')
              AND i.resolved_at <= i.sla_deadline
        )::NUMERIC
        / NULLIF(
            COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed')), 0
        ) * 100, 1
    )                                       AS sla_compliance_pct,
    ROUND(
        AVG(
            CASE WHEN i.status IN ('Resolved', 'Closed') AND i.resolved_at IS NOT NULL
            THEN EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)) / 3600
            END
        ), 1
    )                                       AS avg_resolution_hours
FROM issues i
JOIN sla_rules s ON s.sla_id = i.sla_id
GROUP BY i.priority, s.target_hours
ORDER BY
    CASE i.priority
        WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3 ELSE 4 END;

-- ── Q4: SLA Trend (Monthly Compliance) ───────────────────────────────────────

SELECT
    DATE_TRUNC('month', i.created_at)       AS month,
    COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                            AS resolved_count,
    COUNT(*) FILTER (
        WHERE i.status IN ('Resolved', 'Closed')
          AND i.resolved_at <= i.sla_deadline
    )                                       AS within_sla_count,
    ROUND(
        COUNT(*) FILTER (
            WHERE i.status IN ('Resolved', 'Closed')
              AND i.resolved_at <= i.sla_deadline
        )::NUMERIC
        / NULLIF(
            COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed')), 0
        ) * 100, 1
    )                                       AS sla_compliance_pct
FROM issues i
GROUP BY DATE_TRUNC('month', i.created_at)
ORDER BY month;

-- ── Q5: Currently Breached Issues (Live) ─────────────────────────────────────

SELECT
    i.issue_number,
    i.title,
    d.department_name,
    c.category_name,
    i.priority,
    i.status,
    t.team_name                             AS assigned_team,
    e.employee_name                         AS assigned_agent,
    i.sla_deadline,
    ROUND(
        EXTRACT(EPOCH FROM (NOW() - i.created_at)) / 3600, 1
    )                                       AS elapsed_hours,
    ROUND(
        EXTRACT(EPOCH FROM (NOW() - i.sla_deadline)) / 3600, 1
    )                                       AS hours_overdue
FROM issues i
JOIN departments d    ON d.department_id = i.department_id
JOIN issue_categories c ON c.category_id = i.category_id
LEFT JOIN teams t     ON t.team_id = i.assigned_team_id
LEFT JOIN employees e ON e.employee_id = i.assigned_agent_id
WHERE i.status NOT IN ('Resolved', 'Closed', 'Cancelled')
  AND i.sla_deadline < NOW()
ORDER BY hours_overdue DESC;

-- ── Q6: Average SLA Consumption by Department ────────────────────────────────

SELECT
    d.department_name,
    ROUND(
        AVG(
            CASE WHEN i.sla_deadline IS NOT NULL
            THEN EXTRACT(EPOCH FROM (
                COALESCE(i.resolved_at, NOW()) - i.created_at
            )) / NULLIF(s.target_hours * 3600, 0) * 100
            END
        ), 1
    )                                       AS avg_sla_consumed_pct
FROM issues i
JOIN departments d ON d.department_id = i.department_id
JOIN sla_rules s   ON s.sla_id = i.sla_id
GROUP BY d.department_name
ORDER BY avg_sla_consumed_pct DESC;
