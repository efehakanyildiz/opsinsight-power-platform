-- =============================================================================
-- OpsInsight — Process Intelligence Queries
-- =============================================================================
-- These queries use IssueHistory to reveal process bottlenecks
-- =============================================================================

-- ── Q1: Average Time per Process Stage ───────────────────────────────────────
-- Calculate time spent in each status by joining consecutive history events

WITH status_durations AS (
    SELECT
        h1.issue_id,
        h1.new_status                   AS status,
        h1.change_timestamp             AS entered_at,
        MIN(h2.change_timestamp)        AS exited_at
    FROM issue_history h1
    LEFT JOIN issue_history h2
        ON h2.issue_id = h1.issue_id
       AND h2.change_timestamp > h1.change_timestamp
       AND h2.event_type IN ('StatusChanged', 'Resolved', 'Closed')
    WHERE h1.event_type IN ('StatusChanged', 'Assigned', 'Created')
      AND h1.new_status IS NOT NULL
    GROUP BY h1.issue_id, h1.new_status, h1.change_timestamp
)
SELECT
    status,
    COUNT(*)                                        AS occurrences,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (COALESCE(exited_at, NOW()) - entered_at)) / 3600), 2
    )                                               AS avg_hours_in_status,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY EXTRACT(EPOCH FROM (COALESCE(exited_at, NOW()) - entered_at)) / 3600
        ), 2
    )                                               AS median_hours_in_status,
    ROUND(
        MAX(EXTRACT(EPOCH FROM (COALESCE(exited_at, NOW()) - entered_at)) / 3600), 1
    )                                               AS max_hours_in_status
FROM status_durations
WHERE status NOT IN ('Closed', 'Cancelled')
GROUP BY status
ORDER BY avg_hours_in_status DESC;

-- ── Q2: Waiting Time by Department ────────────────────────────────────────────
-- Identifies which departments spend most time waiting (approval bottleneck)

WITH waiting_periods AS (
    SELECT
        h1.issue_id,
        h1.change_timestamp             AS waiting_start,
        MIN(h2.change_timestamp)        AS waiting_end
    FROM issue_history h1
    LEFT JOIN issue_history h2
        ON h2.issue_id = h1.issue_id
       AND h2.change_timestamp > h1.change_timestamp
       AND h2.previous_status = 'Waiting'
    WHERE h1.new_status = 'Waiting'
    GROUP BY h1.issue_id, h1.change_timestamp
)
SELECT
    d.department_name,
    COUNT(DISTINCT wp.issue_id)             AS issues_with_waiting,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (COALESCE(wp.waiting_end, NOW()) - wp.waiting_start)) / 3600), 2
    )                                       AS avg_waiting_hours,
    ROUND(
        SUM(EXTRACT(EPOCH FROM (COALESCE(wp.waiting_end, NOW()) - wp.waiting_start)) / 3600), 1
    )                                       AS total_waiting_hours
FROM waiting_periods wp
JOIN issues i       ON i.issue_id = wp.issue_id
JOIN departments d  ON d.department_id = i.department_id
GROUP BY d.department_name
ORDER BY avg_waiting_hours DESC;

-- ── Q3: Transfer Frequency by Team ────────────────────────────────────────────
-- Reveals teams that frequently hand off issues (possible capability gap)

SELECT
    t.team_name,
    d.department_name,
    COUNT(*) FILTER (WHERE h.event_type = 'Transferred')   AS total_transfers_out,
    COUNT(DISTINCT h.issue_id) FILTER (WHERE h.event_type = 'Transferred')
                                                            AS issues_transferred,
    ROUND(
        COUNT(*) FILTER (WHERE h.event_type = 'Transferred')::NUMERIC
        / NULLIF(COUNT(DISTINCT i.issue_id), 0), 2
    )                                                       AS avg_transfers_per_issue
FROM issue_history h
JOIN issues i       ON i.issue_id = h.issue_id
JOIN teams t        ON t.team_id = i.assigned_team_id
JOIN departments d  ON d.department_id = t.department_id
GROUP BY t.team_name, d.department_name
ORDER BY avg_transfers_per_issue DESC;

-- ── Q4: Status Change Complexity per Category ─────────────────────────────────
-- More status changes = more complex issue lifecycle

SELECT
    c.category_name,
    d.department_name,
    COUNT(DISTINCT i.issue_id)  AS issue_count,
    ROUND(
        COUNT(h.history_id)::NUMERIC / NULLIF(COUNT(DISTINCT i.issue_id), 0), 1
    )                           AS avg_events_per_issue,
    ROUND(
        COUNT(h.history_id) FILTER (WHERE h.event_type = 'StatusChanged')::NUMERIC
        / NULLIF(COUNT(DISTINCT i.issue_id), 0), 1
    )                           AS avg_status_changes_per_issue
FROM issue_history h
JOIN issues i           ON i.issue_id = h.issue_id
JOIN issue_categories c ON c.category_id = i.category_id
JOIN departments d       ON d.department_id = i.department_id
GROUP BY c.category_name, d.department_name
ORDER BY avg_status_changes_per_issue DESC
LIMIT 20;

-- ── Q5: Process Bottleneck Index ──────────────────────────────────────────────
-- Composite score identifying the most problematic categories
-- Score = (Breach Rate × 40) + (Avg Resolution Hours / SLA Hours × 30) + (Reopen Rate × 30)

WITH category_stats AS (
    SELECT
        c.category_name,
        d.department_name,
        COUNT(*) FILTER (WHERE i.status IN ('Resolved', 'Closed'))
                                            AS resolved_count,
        COUNT(*) FILTER (
            WHERE i.status IN ('Resolved', 'Closed')
              AND i.resolved_at > i.sla_deadline
        )                                   AS breached_count,
        ROUND(
            AVG(EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)) / 3600)
            FILTER (WHERE i.status IN ('Resolved', 'Closed')), 1
        )                                   AS avg_res_hours,
        AVG(s.target_hours)                 AS sla_target_hours,
        COUNT(*) FILTER (WHERE i.reopen_count > 0)
                                            AS reopened_count,
        COUNT(*)                            AS total_issues
    FROM issues i
    JOIN issue_categories c ON c.category_id = i.category_id
    JOIN departments d       ON d.department_id = i.department_id
    LEFT JOIN sla_rules s    ON s.sla_id = i.sla_id
    GROUP BY c.category_name, d.department_name
    HAVING COUNT(*) >= 10  -- Only statistically meaningful categories
)
SELECT
    category_name,
    department_name,
    total_issues,
    resolved_count,
    ROUND(breached_count::NUMERIC / NULLIF(resolved_count, 0) * 100, 1)   AS breach_rate_pct,
    avg_res_hours,
    ROUND(avg_res_hours / NULLIF(sla_target_hours, 0) * 100, 1)           AS resolution_vs_sla_pct,
    ROUND(reopened_count::NUMERIC / NULLIF(resolved_count, 0) * 100, 1)   AS reopen_rate_pct,
    -- Composite bottleneck score (0-100)
    ROUND(
        (breached_count::NUMERIC / NULLIF(resolved_count, 0) * 40)
        + (avg_res_hours / NULLIF(sla_target_hours, 0) * 30)
        + (reopened_count::NUMERIC / NULLIF(resolved_count, 0) * 30), 1
    )                                                                       AS bottleneck_score
FROM category_stats
ORDER BY bottleneck_score DESC
LIMIT 15;

-- ── Q6: Longest Currently Open Issues ────────────────────────────────────────

SELECT
    i.issue_number,
    i.title,
    d.department_name,
    c.category_name,
    i.priority,
    i.status,
    t.team_name,
    ROUND(
        EXTRACT(EPOCH FROM (NOW() - i.created_at)) / 3600, 1
    )                                       AS age_hours,
    ROUND(
        EXTRACT(EPOCH FROM (NOW() - i.created_at)) / 86400, 1
    )                                       AS age_days,
    i.sla_deadline,
    CASE
        WHEN i.sla_deadline < NOW() THEN 'BREACHED'
        WHEN i.sla_deadline < NOW() + INTERVAL '2 hours' THEN 'CRITICAL'
        ELSE 'AT RISK'
    END                                     AS sla_risk
FROM issues i
JOIN departments d    ON d.department_id = i.department_id
JOIN issue_categories c ON c.category_id = i.category_id
LEFT JOIN teams t     ON t.team_id = i.assigned_team_id
WHERE i.status NOT IN ('Resolved', 'Closed', 'Cancelled')
ORDER BY age_hours DESC
LIMIT 20;
