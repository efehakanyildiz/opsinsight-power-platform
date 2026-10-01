-- =============================================================================
-- OpsInsight — Schema Reference (SQL)
-- Northstar Operations Group
-- =============================================================================
-- This script represents the relational schema equivalent of the Dataverse
-- data model. Used for documentation, analytical reference, and local testing.
-- Compatible with: PostgreSQL 14+
-- =============================================================================

-- Enable UUID extension (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- LOOKUP / REFERENCE TABLES
-- =============================================================================

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    department_id   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    department_name VARCHAR(100) NOT NULL,
    department_code VARCHAR(10)  NOT NULL UNIQUE,
    manager         VARCHAR(100),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE departments IS 'Top-level organizational units within Northstar Operations Group';

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    team_id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    team_name       VARCHAR(100) NOT NULL,
    department_id   UUID        NOT NULL REFERENCES departments(department_id),
    team_manager    VARCHAR(100),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE teams IS 'Operational teams responsible for handling issues';

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    employee_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_name   VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    department_id   UUID        NOT NULL REFERENCES departments(department_id),
    team_id         UUID        REFERENCES teams(team_id),
    manager_id      UUID        REFERENCES employees(employee_id),  -- self-reference
    role            VARCHAR(50) NOT NULL
                    CHECK (role IN ('Employee', 'Agent', 'Manager', 'Admin')),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE employees IS 'All Northstar personnel with role-based platform access';

-- Issue Categories
CREATE TABLE IF NOT EXISTS issue_categories (
    category_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name   VARCHAR(100) NOT NULL,
    department_id   UUID        NOT NULL REFERENCES departments(department_id),
    default_team_id UUID        REFERENCES teams(team_id),
    description     VARCHAR(500),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE issue_categories IS 'Issue classification used to determine default routing team';

-- SLA Rules
CREATE TABLE IF NOT EXISTS sla_rules (
    sla_id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    priority                VARCHAR(20) NOT NULL UNIQUE
                            CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    target_hours            DECIMAL(5,1) NOT NULL,
    warning_threshold_pct   INTEGER     NOT NULL DEFAULT 70,
    critical_threshold_pct  INTEGER     NOT NULL DEFAULT 90,
    is_active               BOOLEAN     NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE sla_rules IS 'Configurable SLA target hours and alert thresholds by priority';

-- Root Causes
CREATE TABLE IF NOT EXISTS root_causes (
    root_cause_id   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    root_cause_name VARCHAR(100) NOT NULL,
    category_id     UUID        REFERENCES issue_categories(category_id),
    description     VARCHAR(500)
);

COMMENT ON TABLE root_causes IS 'Classified root causes for resolved issues — enables root cause analysis';

-- Resolution Codes
CREATE TABLE IF NOT EXISTS resolution_codes (
    resolution_code_id  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    resolution_name     VARCHAR(100) NOT NULL,
    description         VARCHAR(500)
);

COMMENT ON TABLE resolution_codes IS 'Standardized resolution types for consistent analytics';

-- =============================================================================
-- CORE TRANSACTIONAL TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS issues (
    issue_id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_number        VARCHAR(20) NOT NULL UNIQUE,  -- OPS-YYYY-NNNN
    title               VARCHAR(200) NOT NULL,
    description         TEXT        NOT NULL,

    -- Submitter
    created_by          UUID        NOT NULL REFERENCES employees(employee_id),
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW(),

    -- Classification
    department_id       UUID        NOT NULL REFERENCES departments(department_id),
    category_id         UUID        NOT NULL REFERENCES issue_categories(category_id),

    -- Assignment
    assigned_team_id    UUID        REFERENCES teams(team_id),
    assigned_agent_id   UUID        REFERENCES employees(employee_id),

    -- Priority & Status
    priority            VARCHAR(20) NOT NULL
                        CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    status              VARCHAR(20) NOT NULL DEFAULT 'New'
                        CHECK (status IN (
                            'New', 'Assigned', 'In Progress', 'Waiting',
                            'Resolved', 'Closed', 'Reopened', 'Cancelled'
                        )),

    -- SLA
    sla_id              UUID        REFERENCES sla_rules(sla_id),
    sla_target_hours    DECIMAL(5,1),
    sla_deadline        TIMESTAMP,
    sla_pct_consumed    DECIMAL(6,2),  -- Updated by scheduled flow
    sla_status          VARCHAR(20)    -- Healthy / Warning / Critical / Breached / Completed

                        CHECK (sla_status IN ('Healthy','Warning','Critical','Breached','Completed')),

    -- Timestamps
    first_response_at   TIMESTAMP,
    resolved_at         TIMESTAMP,
    closed_at           TIMESTAMP,
    last_updated_at     TIMESTAMP   NOT NULL DEFAULT NOW(),

    -- Resolution
    root_cause_id       UUID        REFERENCES root_causes(root_cause_id),
    resolution_code_id  UUID        REFERENCES resolution_codes(resolution_code_id),
    resolution_summary  TEXT,

    -- Tracking
    reopen_count        INTEGER     NOT NULL DEFAULT 0
                        CHECK (reopen_count >= 0),

    -- Integrity checks
    CONSTRAINT chk_resolved_after_created
        CHECK (resolved_at IS NULL OR resolved_at >= created_at),
    CONSTRAINT chk_closed_after_resolved
        CHECK (closed_at IS NULL OR resolved_at IS NULL OR closed_at >= resolved_at),
    CONSTRAINT chk_deadline_after_created
        CHECK (sla_deadline IS NULL OR sla_deadline >= created_at)
);

COMMENT ON TABLE issues IS 'Core transactional table — every operational issue raised in the platform';

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_issues_status
    ON issues(status);

CREATE INDEX IF NOT EXISTS idx_issues_priority
    ON issues(priority);

CREATE INDEX IF NOT EXISTS idx_issues_assigned_team
    ON issues(assigned_team_id);

CREATE INDEX IF NOT EXISTS idx_issues_created_by
    ON issues(created_by);

CREATE INDEX IF NOT EXISTS idx_issues_sla_deadline
    ON issues(sla_deadline);

CREATE INDEX IF NOT EXISTS idx_issues_created_at
    ON issues(created_at);

CREATE INDEX IF NOT EXISTS idx_issues_department
    ON issues(department_id);

-- =============================================================================
-- EVENT LOG TABLE (Process Intelligence Core)
-- =============================================================================

CREATE TABLE IF NOT EXISTS issue_history (
    history_id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id            UUID        NOT NULL REFERENCES issues(issue_id),
    event_type          VARCHAR(50) NOT NULL
                        CHECK (event_type IN (
                            'Created', 'Assigned', 'StatusChanged', 'PriorityChanged',
                            'Transferred', 'Escalated', 'Resolved', 'Closed',
                            'Reopened', 'CommentAdded'
                        )),
    previous_status     VARCHAR(20),
    new_status          VARCHAR(20),
    previous_team       VARCHAR(100),
    new_team            VARCHAR(100),
    changed_by          VARCHAR(100),  -- EmployeeId or 'SYSTEM'
    change_timestamp    TIMESTAMP   NOT NULL DEFAULT NOW(),
    notes               TEXT
);

COMMENT ON TABLE issue_history IS
    'Append-only event log of all issue changes — core of process intelligence analytics';

CREATE INDEX IF NOT EXISTS idx_history_issue_id
    ON issue_history(issue_id);

CREATE INDEX IF NOT EXISTS idx_history_timestamp
    ON issue_history(change_timestamp);

CREATE INDEX IF NOT EXISTS idx_history_event_type
    ON issue_history(event_type);

-- =============================================================================
-- SUPPORTING TABLES
-- =============================================================================

-- Issue Comments
CREATE TABLE IF NOT EXISTS issue_comments (
    comment_id      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id        UUID        NOT NULL REFERENCES issues(issue_id),
    comment_text    TEXT        NOT NULL,
    comment_author  UUID        NOT NULL REFERENCES employees(employee_id),
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    is_internal     BOOLEAN     NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE issue_comments IS 'Threaded comments on issues — internal and external';

CREATE INDEX IF NOT EXISTS idx_comments_issue_id
    ON issue_comments(issue_id);

-- Escalations
CREATE TABLE IF NOT EXISTS escalations (
    escalation_id   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id        UUID        NOT NULL REFERENCES issues(issue_id),
    escalation_level INTEGER    NOT NULL CHECK (escalation_level IN (1, 2)),
    escalated_to    UUID        NOT NULL REFERENCES employees(employee_id),
    reason          TEXT        NOT NULL,
    escalated_at    TIMESTAMP   NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMP
);

COMMENT ON TABLE escalations IS
    'SLA breach escalations — Level 1 (Team Manager) and Level 2 (Dept Manager)';

CREATE INDEX IF NOT EXISTS idx_escalations_issue_id
    ON escalations(issue_id);

-- =============================================================================
-- REFERENCE DATA (Seed Values)
-- =============================================================================

INSERT INTO departments (department_name, department_code, manager)
VALUES
    ('Information Technology', 'IT',    'Sarah Mitchell'),
    ('Finance',                'FIN',   'David Thompson'),
    ('Human Resources',        'HR',    'Emma Clarke'),
    ('Procurement',            'PROC',  'Robert Hughes'),
    ('Operations',             'OPS',   'Linda Foster'),
    ('Sales Operations',       'SALES', 'Mark Patterson')
ON CONFLICT (department_code) DO NOTHING;

INSERT INTO sla_rules (priority, target_hours, warning_threshold_pct, critical_threshold_pct)
VALUES
    ('Critical', 4,  70, 90),
    ('High',     8,  70, 90),
    ('Medium',   24, 70, 90),
    ('Low',      72, 70, 90)
ON CONFLICT (priority) DO NOTHING;

INSERT INTO root_causes (root_cause_name, description)
VALUES
    ('Incorrect Configuration', 'System or process configuration was incorrect'),
    ('Missing Approval',        'Required approval was not obtained before proceeding'),
    ('Data Quality',            'Incorrect, incomplete or duplicate data'),
    ('User Error',              'Incorrect user action caused the issue'),
    ('System Integration',      'Integration between systems failed or was misconfigured'),
    ('Capacity',                'Insufficient resources or bandwidth to handle demand'),
    ('Vendor Dependency',       'Third-party vendor failed to deliver or respond'),
    ('Process Design',          'Existing process design caused or contributed to the issue'),
    ('Missing Information',     'Required information was unavailable or not provided'),
    ('Access Rights',           'Incorrect or missing access permissions')
ON CONFLICT DO NOTHING;

INSERT INTO resolution_codes (resolution_name, description)
VALUES
    ('Configuration Updated',     'System or process configuration was corrected'),
    ('Data Corrected',            'Incorrect data was identified and corrected'),
    ('User Guidance Provided',    'User was guided through the correct process'),
    ('Process Updated',           'Process was redesigned or updated to prevent recurrence'),
    ('Access Granted',            'Required access permissions were provisioned'),
    ('Vendor Resolved',           'Vendor resolved the underlying issue'),
    ('Duplicate Request',         'Issue was a duplicate of an existing request'),
    ('No Action Required',        'Investigation found no action was necessary'),
    ('Escalated to Third Party',  'Issue was escalated to an external party for resolution')
ON CONFLICT DO NOTHING;
