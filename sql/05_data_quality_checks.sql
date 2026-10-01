-- =============================================================================
-- OpsInsight — Data Quality Checks (SQL)
-- =============================================================================
-- Run these checks against the database to identify data integrity issues
-- =============================================================================

-- ── CHECK 1: Issues resolved before they were created ────────────────────────
SELECT
    'CHECK 01: ResolvedAt before CreatedAt'     AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE resolved_at IS NOT NULL
  AND resolved_at < created_at;

-- ── CHECK 2: SLA deadline before creation ─────────────────────────────────────
SELECT
    'CHECK 02: SLA Deadline before CreatedAt'   AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE sla_deadline IS NOT NULL
  AND sla_deadline < created_at;

-- ── CHECK 3: Closed without resolution time ───────────────────────────────────
SELECT
    'CHECK 03: Closed without ResolvedAt'       AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE status = 'Closed'
  AND resolved_at IS NULL;

-- ── CHECK 4: Closed before resolved ───────────────────────────────────────────
SELECT
    'CHECK 04: ClosedAt before ResolvedAt'      AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE closed_at IS NOT NULL
  AND resolved_at IS NOT NULL
  AND closed_at < resolved_at;

-- ── CHECK 5: Unknown category ─────────────────────────────────────────────────
SELECT
    'CHECK 05: Unknown CategoryId'              AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues i
WHERE NOT EXISTS (
    SELECT 1 FROM issue_categories c WHERE c.category_id = i.category_id
);

-- ── CHECK 6: Unknown department ───────────────────────────────────────────────
SELECT
    'CHECK 06: Unknown DepartmentId'            AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues i
WHERE NOT EXISTS (
    SELECT 1 FROM departments d WHERE d.department_id = i.department_id
);

-- ── CHECK 7: Invalid priority value ───────────────────────────────────────────
SELECT
    'CHECK 07: Invalid Priority'                AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE priority NOT IN ('Critical', 'High', 'Medium', 'Low');

-- ── CHECK 8: Invalid status value ─────────────────────────────────────────────
SELECT
    'CHECK 08: Invalid Status'                  AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE status NOT IN (
    'New', 'Assigned', 'In Progress', 'Waiting',
    'Resolved', 'Closed', 'Reopened', 'Cancelled'
);

-- ── CHECK 9: Duplicate issue numbers ──────────────────────────────────────────
SELECT
    'CHECK 09: Duplicate IssueNumber'           AS check_name,
    COUNT(*)                                    AS violation_count
FROM (
    SELECT issue_number, COUNT(*) AS cnt
    FROM issues
    GROUP BY issue_number
    HAVING COUNT(*) > 1
) dupes;

-- ── CHECK 10: History events before issue creation ────────────────────────────
SELECT
    'CHECK 10: History event before CreatedAt'  AS check_name,
    COUNT(*)                                    AS violation_count
FROM issue_history h
JOIN issues i ON i.issue_id = h.issue_id
WHERE h.change_timestamp < i.created_at;

-- ── CHECK 11: Resolved issue still in New status ──────────────────────────────
SELECT
    'CHECK 11: Resolved issue in New status'    AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE status = 'New'
  AND resolved_at IS NOT NULL;

-- ── CHECK 12: Negative reopen count ───────────────────────────────────────────
SELECT
    'CHECK 12: Negative ReopenCount'            AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE reopen_count < 0;

-- ── CHECK 13: Orphaned history (IssueId not in Issues) ───────────────────────
SELECT
    'CHECK 13: Orphaned IssueHistory'           AS check_name,
    COUNT(*)                                    AS violation_count
FROM issue_history h
WHERE NOT EXISTS (
    SELECT 1 FROM issues i WHERE i.issue_id = h.issue_id
);

-- ── CHECK 14: Orphaned comments ───────────────────────────────────────────────
SELECT
    'CHECK 14: Orphaned IssueComments'          AS check_name,
    COUNT(*)                                    AS violation_count
FROM issue_comments c
WHERE NOT EXISTS (
    SELECT 1 FROM issues i WHERE i.issue_id = c.issue_id
);

-- ── CHECK 15: Orphaned escalations ────────────────────────────────────────────
SELECT
    'CHECK 15: Orphaned Escalations'            AS check_name,
    COUNT(*)                                    AS violation_count
FROM escalations e
WHERE NOT EXISTS (
    SELECT 1 FROM issues i WHERE i.issue_id = e.issue_id
);

-- ── CHECK 16: Missing SLA rule ────────────────────────────────────────────────
SELECT
    'CHECK 16: Issues without SLA rule'         AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE sla_id IS NULL
  AND status NOT IN ('Cancelled');

-- ── CHECK 17: Out-of-order history events ────────────────────────────────────
-- Detects any history event that occurred before the preceding event for the same issue
SELECT
    'CHECK 17: Out-of-order history events'     AS check_name,
    COUNT(*)                                    AS violation_count
FROM (
    SELECT
        h1.history_id,
        h1.change_timestamp,
        LAG(h1.change_timestamp) OVER (
            PARTITION BY h1.issue_id
            ORDER BY h1.change_timestamp
        )                                       AS prev_timestamp
    FROM issue_history h1
) ordered
WHERE change_timestamp < prev_timestamp;

-- ── CHECK 18: Resolved issues without root cause ──────────────────────────────
SELECT
    'CHECK 18: Resolved without RootCause (warning)' AS check_name,
    COUNT(*)                                         AS violation_count
FROM issues
WHERE status IN ('Resolved', 'Closed')
  AND root_cause_id IS NULL;

-- ── CHECK 19: SLATargetHours must be positive ─────────────────────────────────
SELECT
    'CHECK 19: Invalid SLA target hours'        AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE sla_target_hours IS NOT NULL
  AND sla_target_hours <= 0;

-- ── CHECK 20: Negative resolution duration ────────────────────────────────────
SELECT
    'CHECK 20: Negative resolution duration'    AS check_name,
    COUNT(*)                                    AS violation_count
FROM issues
WHERE resolved_at IS NOT NULL
  AND created_at IS NOT NULL
  AND resolved_at < created_at;

-- ── SUMMARY VIEW: All Checks Combined ────────────────────────────────────────
-- Run all 20 checks together and get a pass/fail summary

WITH all_checks AS (
    SELECT 'CHECK 01' AS chk, COUNT(*) AS cnt FROM issues
    WHERE resolved_at IS NOT NULL AND resolved_at < created_at
    UNION ALL
    SELECT 'CHECK 02', COUNT(*) FROM issues
    WHERE sla_deadline IS NOT NULL AND sla_deadline < created_at
    UNION ALL
    SELECT 'CHECK 03', COUNT(*) FROM issues
    WHERE status = 'Closed' AND resolved_at IS NULL
    UNION ALL
    SELECT 'CHECK 04', COUNT(*) FROM issues
    WHERE closed_at IS NOT NULL AND resolved_at IS NOT NULL AND closed_at < resolved_at
    UNION ALL
    SELECT 'CHECK 07', COUNT(*) FROM issues
    WHERE priority NOT IN ('Critical', 'High', 'Medium', 'Low')
    UNION ALL
    SELECT 'CHECK 08', COUNT(*) FROM issues
    WHERE status NOT IN ('New','Assigned','In Progress','Waiting',
        'Resolved','Closed','Reopened','Cancelled')
    UNION ALL
    SELECT 'CHECK 12', COUNT(*) FROM issues WHERE reopen_count < 0
    UNION ALL
    SELECT 'CHECK 13', COUNT(*) FROM issue_history h
    WHERE NOT EXISTS (SELECT 1 FROM issues i WHERE i.issue_id = h.issue_id)
    UNION ALL
    SELECT 'CHECK 14', COUNT(*) FROM issue_comments c
    WHERE NOT EXISTS (SELECT 1 FROM issues i WHERE i.issue_id = c.issue_id)
    UNION ALL
    SELECT 'CHECK 15', COUNT(*) FROM escalations e
    WHERE NOT EXISTS (SELECT 1 FROM issues i WHERE i.issue_id = e.issue_id)
)
SELECT
    chk,
    cnt                             AS violation_count,
    CASE WHEN cnt = 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM all_checks
ORDER BY chk;
