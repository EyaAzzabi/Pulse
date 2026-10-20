BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> f015181238ee

CREATE TABLE organizations (
    name VARCHAR(255) NOT NULL, 
    industry VARCHAR(64) NOT NULL, 
    country VARCHAR(64) NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    company_size VARCHAR(32) NOT NULL, 
    timezone VARCHAR(64) NOT NULL, 
    is_demo BOOLEAN NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE users (
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    full_name VARCHAR(255) NOT NULL, 
    preferred_language VARCHAR(10) NOT NULL, 
    default_currency VARCHAR(3) NOT NULL, 
    timezone VARCHAR(64) NOT NULL, 
    is_active BOOLEAN NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE action_proposals (
    organization_id VARCHAR(36) NOT NULL, 
    created_by_user_id VARCHAR(36) NOT NULL, 
    action_type VARCHAR(64) NOT NULL, 
    target_json TEXT NOT NULL, 
    details_json TEXT NOT NULL, 
    expected_result TEXT NOT NULL, 
    risks TEXT NOT NULL, 
    evidence_json TEXT NOT NULL, 
    requires_approval BOOLEAN NOT NULL, 
    status VARCHAR(32) NOT NULL, 
    approved_by_user_id VARCHAR(36), 
    approved_at VARCHAR(32), 
    execution_result_json TEXT NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by_user_id) REFERENCES users (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_action_proposals_organization_id ON action_proposals (organization_id);

CREATE TABLE audit_logs (
    organization_id VARCHAR(36) NOT NULL, 
    actor_user_id VARCHAR(36), 
    event_type VARCHAR(64) NOT NULL, 
    details_json TEXT NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_audit_logs_organization_id ON audit_logs (organization_id);

CREATE TABLE business_profiles (
    organization_id VARCHAR(36) NOT NULL, 
    monthly_revenue_estimate NUMERIC(14, 2) NOT NULL, 
    monthly_fixed_expenses_estimate NUMERIC(14, 2) NOT NULL, 
    current_cash_balance NUMERIC(14, 2) NOT NULL, 
    customer_payment_delay_days INTEGER NOT NULL, 
    supplier_payment_delay_days INTEGER NOT NULL, 
    employee_count INTEGER NOT NULL, 
    payroll_frequency VARCHAR(16) NOT NULL, 
    risk_tolerance VARCHAR(16) NOT NULL, 
    alert_sensitivity VARCHAR(16) NOT NULL, 
    forecast_horizon_days INTEGER NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id), 
    UNIQUE (organization_id)
);

CREATE TABLE conversations (
    organization_id VARCHAR(36) NOT NULL, 
    user_id VARCHAR(36) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_conversations_organization_id ON conversations (organization_id);

CREATE INDEX ix_conversations_user_id ON conversations (user_id);

CREATE TABLE forecast_runs (
    organization_id VARCHAR(36) NOT NULL, 
    horizon_days INTEGER NOT NULL, 
    method VARCHAR(32) NOT NULL, 
    assumptions_json TEXT NOT NULL, 
    starting_cash NUMERIC(14, 2) NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_forecast_runs_organization_id ON forecast_runs (organization_id);

CREATE TABLE invoices (
    organization_id VARCHAR(36) NOT NULL, 
    direction VARCHAR(16) NOT NULL, 
    counterparty_name VARCHAR(255) NOT NULL, 
    amount NUMERIC(14, 2) NOT NULL, 
    amount_paid NUMERIC(14, 2) NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    issue_date DATE NOT NULL, 
    due_date DATE NOT NULL, 
    status VARCHAR(16) NOT NULL, 
    reference VARCHAR(64) NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_invoices_due_date ON invoices (due_date);

CREATE INDEX ix_invoices_organization_id ON invoices (organization_id);

CREATE TABLE memberships (
    user_id VARCHAR(36) NOT NULL, 
    organization_id VARCHAR(36) NOT NULL, 
    role VARCHAR(32) NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_memberships_organization_id ON memberships (organization_id);

CREATE INDEX ix_memberships_user_id ON memberships (user_id);

CREATE TABLE notifications (
    organization_id VARCHAR(36) NOT NULL, 
    user_id VARCHAR(36), 
    category VARCHAR(64) NOT NULL, 
    severity VARCHAR(16) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    body TEXT NOT NULL, 
    link VARCHAR(255) NOT NULL, 
    read BOOLEAN NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_notifications_organization_id ON notifications (organization_id);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE TABLE onboarding_progress (
    organization_id VARCHAR(36) NOT NULL, 
    current_step INTEGER NOT NULL, 
    completed BOOLEAN NOT NULL, 
    data_json VARCHAR NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id), 
    UNIQUE (organization_id)
);

CREATE TABLE recommendations (
    organization_id VARCHAR(36) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    rationale TEXT NOT NULL, 
    expected_impact TEXT NOT NULL, 
    risk_level VARCHAR(16) NOT NULL, 
    requires_approval BOOLEAN NOT NULL, 
    status VARCHAR(32) NOT NULL, 
    evidence_json TEXT NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_recommendations_organization_id ON recommendations (organization_id);

CREATE TABLE recurring_obligations (
    organization_id VARCHAR(36) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    amount NUMERIC(14, 2) NOT NULL, 
    category VARCHAR(64) NOT NULL, 
    frequency VARCHAR(16) NOT NULL, 
    next_due_date DATE NOT NULL, 
    direction VARCHAR(8) NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_recurring_obligations_organization_id ON recurring_obligations (organization_id);

CREATE TABLE simulation_scenarios (
    organization_id VARCHAR(36) NOT NULL, 
    created_by_user_id VARCHAR(36) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    assumptions_json TEXT NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by_user_id) REFERENCES users (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_simulation_scenarios_organization_id ON simulation_scenarios (organization_id);

CREATE TABLE transactions (
    organization_id VARCHAR(36) NOT NULL, 
    date DATE NOT NULL, 
    amount NUMERIC(14, 2) NOT NULL, 
    currency VARCHAR(3) NOT NULL, 
    category VARCHAR(64) NOT NULL, 
    direction VARCHAR(8) NOT NULL, 
    source VARCHAR(32) NOT NULL, 
    status VARCHAR(16) NOT NULL, 
    description VARCHAR(255) NOT NULL, 
    import_reference VARCHAR(128), 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id)
);

CREATE INDEX ix_transactions_date ON transactions (date);

CREATE INDEX ix_transactions_organization_id ON transactions (organization_id);

CREATE TABLE chat_messages (
    conversation_id VARCHAR(36) NOT NULL, 
    role VARCHAR(16) NOT NULL, 
    content TEXT NOT NULL, 
    metadata_json TEXT NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);

CREATE INDEX ix_chat_messages_conversation_id ON chat_messages (conversation_id);

CREATE TABLE forecast_points (
    forecast_run_id VARCHAR(36) NOT NULL, 
    date DATE NOT NULL, 
    projected_cash NUMERIC(14, 2) NOT NULL, 
    known_component NUMERIC(14, 2) NOT NULL, 
    uncertain_component NUMERIC(14, 2) NOT NULL, 
    confidence VARCHAR(16) NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(forecast_run_id) REFERENCES forecast_runs (id)
);

CREATE INDEX ix_forecast_points_date ON forecast_points (date);

CREATE INDEX ix_forecast_points_forecast_run_id ON forecast_points (forecast_run_id);

CREATE TABLE simulation_results (
    scenario_id VARCHAR(36) NOT NULL, 
    lowest_cash_point NUMERIC(14, 2) NOT NULL, 
    lowest_cash_date VARCHAR(32) NOT NULL, 
    runway_days INTEGER, 
    days_below_zero INTEGER NOT NULL, 
    impact_vs_baseline_json TEXT NOT NULL, 
    baseline_points_json TEXT NOT NULL, 
    simulated_points_json TEXT NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(scenario_id) REFERENCES simulation_scenarios (id)
);

CREATE UNIQUE INDEX ix_simulation_results_scenario_id ON simulation_results (scenario_id);

INSERT INTO alembic_version (version_num) VALUES ('f015181238ee') RETURNING alembic_version.version_num;

-- Running upgrade f015181238ee -> 8aaa48b081f8

CREATE TABLE email_otps (
    email VARCHAR(255) NOT NULL, 
    code_hash VARCHAR(64) NOT NULL, 
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    attempts INTEGER NOT NULL, 
    consumed BOOLEAN NOT NULL, 
    id VARCHAR(36) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_email_otps_email ON email_otps (email);

UPDATE alembic_version SET version_num='8aaa48b081f8' WHERE alembic_version.version_num = 'f015181238ee';

COMMIT;

