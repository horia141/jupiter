"""Reset initial migrations

Revision ID: 5c7e6a943950
Revises: None
Create Date: 2022-02-24 20:33:38.662929

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5c7e6a943950'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
CREATE TABLE use_case_mutation_use_case_invocation_record (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    name VARCHAR NOT NULL, 
    args JSON NOT NULL, 
    result VARCHAR NOT NULL, 
    error_str VARCHAR, 
    PRIMARY KEY (owner_ref_id, timestamp, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""  
CREATE TABLE workspace (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    name VARCHAR(100) NOT NULL, 
    timezone VARCHAR(100) NOT NULL, 
    default_project_ref_id INTEGER, 
    PRIMARY KEY (ref_id)
);""")
    op.execute("""  
CREATE TABLE workspace_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE TABLE vacation_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""  
CREATE UNIQUE INDEX ix_vacation_collection_workspace_ref_id ON vacation_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE vacation_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES vacation_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE vacation (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    name VARCHAR(100) NOT NULL, 
    start_date DATETIME NOT NULL, 
    end_date DATETIME NOT NULL, 
    vacation_collection_ref_id INTEGER NOT NULL, 
    CONSTRAINT pk_vacation PRIMARY KEY (ref_id), 
    CONSTRAINT fk_vacation_vacation_collection_ref_id_vacation_collection FOREIGN KEY(vacation_collection_ref_id) REFERENCES vacation_collection (ref_id)
);""")
    op.execute("""  
CREATE INDEX ix_vacation_vacation_collection_ref_id ON vacation (vacation_collection_ref_id);""")
    op.execute("""
CREATE TABLE vacation_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES vacation (ref_id)
);""")
    op.execute("""
CREATE TABLE project_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""  
CREATE UNIQUE INDEX ix_project_collection_workspace_ref_id ON project_collection (workspace_ref_id);""")
    op.execute("""  
CREATE TABLE project_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES project_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE project (
    ref_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    archived BOOLEAN NOT NULL,
    created_time DATETIME NOT NULL,
    last_modified_time DATETIME NOT NULL,
    archived_time DATETIME,
    project_collection_ref_id INTEGER NOT NULL,
    the_key VARCHAR(32) NOT NULL,
    name VARCHAR(100) NOT NULL, 
    notion_link_uuid VARCHAR(16),
    PRIMARY KEY (ref_id),
    FOREIGN KEY(project_collection_ref_id) REFERENCES project_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE project_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES project (ref_id)
);""")
    op.execute("""
CREATE TABLE inbox_task_collection (
    ref_id INTEGER NOT NULL, 
    workspace_ref_id INTEGER, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    CONSTRAINT pk_inbox_task_collection PRIMARY KEY (ref_id), 
    CONSTRAINT fk_inbox_task_collection_workspace_ref_id_workspace FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_inbox_task_collection_workspace_ref_id ON inbox_task_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE inbox_task_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES inbox_task_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE inbox_task (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    inbox_task_collection_ref_id INTEGER NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    project_ref_id INTEGER,
    habit_ref_id INTEGER, 
    chore_ref_id INTEGER, 
    big_plan_ref_id INTEGER, 
    metric_ref_id INTEGER, 
    person_ref_id INTEGER, 
    name VARCHAR NOT NULL, 
    status VARCHAR(16) NOT NULL, 
    eisen VARCHAR(20) NOT NULL, 
    difficulty VARCHAR(10), 
    actionable_date DATETIME, 
    due_date DATETIME, 
    recurring_timeline VARCHAR, 
    recurring_repeat_index INTEGER, 
    recurring_gen_right_now DATETIME, 
    accepted_time DATETIME, 
    working_time DATETIME, 
    completed_time DATETIME,  
    CONSTRAINT pk_inbox_task PRIMARY KEY (ref_id), 
    CONSTRAINT fk_inbox_task_inbox_task_collection_ref_id_inbox_task_collection FOREIGN KEY(inbox_task_collection_ref_id) REFERENCES inbox_task_collection (ref_id),
    CONSTRAINT fk_inbox_task_project_ref_id_project FOREIGN KEY(project_ref_id) REFERENCES project (ref_id),  
    CONSTRAINT fk_inbox_task_habit_ref_id_habit FOREIGN KEY(habit_ref_id) REFERENCES habit (ref_id), 
    CONSTRAINT fk_inbox_task_chore_ref_id_chore FOREIGN KEY(chore_ref_id) REFERENCES chore (ref_id), 
    CONSTRAINT fk_inbox_task_big_plan_ref_id_big_plan FOREIGN KEY(big_plan_ref_id) REFERENCES big_plan (ref_id),
    CONSTRAINT fk_inbox_task_metric_ref_id_metric FOREIGN KEY(metric_ref_id) REFERENCES metric (ref_id), 
    CONSTRAINT fk_inbox_task_person_ref_id_person FOREIGN KEY(person_ref_id) REFERENCES person (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_inbox_task_inbox_task_collection_ref_id ON inbox_task (inbox_task_collection_ref_id);""")
    op.execute("""
CREATE INDEX ix_inbox_task_project_ref_id ON inbox_task (project_ref_id);""")
    op.execute("""
CREATE INDEX ix_inbox_task_habit_ref_id ON inbox_task (habit_ref_id);""")
    op.execute("""
CREATE INDEX ix_inbox_task_chore_ref_id ON inbox_task (chore_ref_id);""")
    op.execute("""
CREATE INDEX ix_inbox_task_person_ref_id ON inbox_task (person_ref_id);""")
    op.execute("""
CREATE INDEX ix_inbox_task_big_plan_ref_id ON inbox_task (big_plan_ref_id);""")
    op.execute("""
CREATE INDEX ix_inbox_task_metric_ref_id ON inbox_task (metric_ref_id);""")
    op.execute("""
CREATE TABLE inbox_task_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES inbox_task (ref_id)
);""")
    op.execute("""
CREATE TABLE habit_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE UNIQUE INDEX ix_habit_collection_workspace_ref_id ON habit_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE habit_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES habit_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE habit (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    habit_collection_ref_id INTEGER NOT NULL, 
    project_ref_id INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    gen_params_period VARCHAR NOT NULL, 
    gen_params_eisen VARCHAR, 
    gen_params_difficulty VARCHAR, 
    gen_params_actionable_from_day INTEGER, 
    gen_params_actionable_from_month INTEGER, 
    gen_params_due_at_time VARCHAR, 
    gen_params_due_at_day INTEGER, 
    gen_params_due_at_month INTEGER, 
    suspended BOOLEAN NOT NULL, 
    skip_rule VARCHAR, 
    repeats_in_period_count INTEGER, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(habit_collection_ref_id) REFERENCES habit_collection (ref_id),
    FOREIGN KEY(project_ref_id) REFERENCES project (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_habit_habit_collection_ref_id ON habit (habit_collection_ref_id);""")
    op.execute("""
CREATE INDEX ix_habit_project_ref_id ON habit (project_ref_id);""")
    op.execute("""
CREATE TABLE habit_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES habit (ref_id)
);""")
    op.execute("""
CREATE TABLE chore_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE UNIQUE INDEX ix_chore_collection_workspace_ref_id ON chore_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE chore_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES chore_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE chore (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    chore_collection_ref_id INTEGER NOT NULL, 
    project_ref_id INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    gen_params_period VARCHAR NOT NULL, 
    gen_params_eisen VARCHAR, 
    gen_params_difficulty VARCHAR, 
    gen_params_actionable_from_day INTEGER, 
    gen_params_actionable_from_month INTEGER, 
    gen_params_due_at_time VARCHAR, 
    gen_params_due_at_day INTEGER, 
    gen_params_due_at_month INTEGER, 
    suspended BOOLEAN NOT NULL, 
    must_do BOOLEAN NOT NULL, 
    skip_rule VARCHAR, 
    start_at_date DATETIME NOT NULL, 
    end_at_date DATETIME, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(chore_collection_ref_id) REFERENCES chore_collection (ref_id), 
    FOREIGN KEY(project_ref_id) REFERENCES project (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_chore_chore_collection_ref_id ON chore (chore_collection_ref_id);""")
    op.execute("""
CREATE INDEX ix_chore_project_ref_id ON chore (project_ref_id);""")
    op.execute("""
CREATE TABLE chore_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES chore (ref_id)
);""")
    op.execute("""
CREATE TABLE big_plan_collection (
    ref_id INTEGER NOT NULL, 
    workspace_ref_id INTEGER, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    CONSTRAINT pk_big_plan_collection PRIMARY KEY (ref_id), 
    CONSTRAINT fk_recurring_task_collection_workspace_ref_id_workspace FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_big_plan_collection_workspace_ref_id ON big_plan_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE big_plan_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES big_plan_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE big_plan (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    big_plan_collection_ref_id INTEGER NOT NULL, 
    project_ref_id INTEGER, 
    name VARCHAR NOT NULL, 
    status VARCHAR(16) NOT NULL, 
    actionable_date DATETIME, 
    due_date DATETIME, 
    notion_link_uuid VARCHAR(16) NOT NULL, 
    accepted_time DATETIME, 
    working_time DATETIME, 
    completed_time DATETIME, 
    CONSTRAINT pk_big_plan PRIMARY KEY (ref_id), 
    CONSTRAINT fk_big_plan_big_plan_collection_ref_id_big_plan_collection FOREIGN KEY(big_plan_collection_ref_id) REFERENCES big_plan_collection (ref_id), 
    CONSTRAINT fk_big_plan_project_ref_id_project FOREIGN KEY(project_ref_id) REFERENCES project (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_big_plan_big_plan_collection_ref_id ON big_plan (big_plan_collection_ref_id);""")
    op.execute("""
CREATE INDEX ix_big_plan_project_ref_id ON big_plan (project_ref_id);""")
    op.execute("""
CREATE TABLE big_plan_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES big_plan (ref_id)
);""")
    op.execute("""
CREATE TABLE smart_list_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE UNIQUE INDEX ix_smart_list_collection_workspace_ref_id ON smart_list_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE smart_list_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES smart_list_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE smart_list (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    smart_list_collection_ref_id INTEGER, 
    the_key VARCHAR(32) NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    icon VARCHAR(1), 
    CONSTRAINT pk_smart_list PRIMARY KEY (ref_id), 
    CONSTRAINT fk_smart_list_smart_list_collection_ref_id_smart_list_collection FOREIGN KEY(smart_list_collection_ref_id) REFERENCES smart_list_collection (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_smart_list_smart_list_collection_ref_id ON smart_list (smart_list_collection_ref_id);""")
    op.execute("""
CREATE TABLE smart_list_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES smart_list (ref_id)
);""")
    op.execute("""
CREATE TABLE smart_list_tag (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    smart_list_ref_id INTEGER NOT NULL, 
    tag_name VARCHAR(100) NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(smart_list_ref_id) REFERENCES smart_list (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_smart_list_tag_smart_list_ref_id ON smart_list_tag (smart_list_ref_id);""")
    op.execute("""
CREATE TABLE smart_list_tag_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES smart_list_tag (ref_id)
);""")
    op.execute("""
CREATE TABLE smart_list_item (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    smart_list_ref_id INTEGER NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    is_done BOOLEAN NOT NULL, 
    tags_ref_id JSON NOT NULL, 
    url VARCHAR, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(smart_list_ref_id) REFERENCES smart_list (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_smart_list_item_smart_list_ref_id ON smart_list_item (smart_list_ref_id);""")
    op.execute("""
CREATE TABLE smart_list_item_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES smart_list (ref_id)
);""")
    op.execute("""
CREATE TABLE metric_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, collection_project_ref_id integer, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE UNIQUE INDEX ix_metric_collection_workspace_ref_id ON metric_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE metric_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES metric_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE metric (
    ref_id INTEGER NOT NULL, 
    version INTEGER, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    metric_collection_ref_id INTEGER, 
    the_key VARCHAR(64) NOT NULL, 
    name VARCHAR NOT NULL, 
    metric_unit VARCHAR, 
    collection_period VARCHAR, 
    collection_project_ref_id INTEGER, 
    collection_eisen VARCHAR, 
    collection_difficulty VARCHAR, 
    collection_actionable_from_day INTEGER, 
    collection_actionable_from_month INTEGER, 
    collection_due_at_time VARCHAR, 
    collection_due_at_day INTEGER, 
    collection_due_at_month INTEGER, 
    icon VARCHAR(1), 
    CONSTRAINT pk_metric PRIMARY KEY (ref_id), 
    CONSTRAINT fk_metric_metric_collection_ref_id_metric_collection FOREIGN KEY(metric_collection_ref_id) REFERENCES metric_collection (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_metric_metric_collection_ref_id ON metric (metric_collection_ref_id);""")
    op.execute("""
CREATE TABLE metric_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES metric (ref_id)
);""")
    op.execute("""
CREATE TABLE metric_entry (
    ref_id INTEGER NOT NULL, 
    version INTEGER, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    metric_ref_id INTEGER NOT NULL, 
    collection_time DATETIME NOT NULL, 
    value FLOAT NOT NULL, 
    notes TEXT,
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(metric_ref_id) REFERENCES metric (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_metric_entry_metric_ref_id ON metric_entry (metric_ref_id);""")
    op.execute("""
CREATE TABLE metric_entry_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON,
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES metric_entry (ref_id)
);""")
    op.execute("""
CREATE TABLE person_collection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    catch_up_project_ref_id INTEGER NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id),
    FOREIGN KEY (catch_up_project_ref_id) REFERENCES project (ref_id)
);""")
    op.execute("""
CREATE UNIQUE INDEX ix_person_collection_workspace_ref_id ON person_collection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE person_collection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES person_collection (ref_id)
);""")
    op.execute("""
CREATE TABLE person (
    ref_id INTEGER NOT NULL, 
    version INTEGER, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    person_collection_ref_id INTEGER, 
    name VARCHAR NOT NULL, 
    relationship VARCHAR NOT NULL, 
    catch_up_project_ref_id INTEGER, 
    catch_up_period VARCHAR, 
    catch_up_eisen VARCHAR, 
    catch_up_difficulty VARCHAR, 
    catch_up_actionable_from_day INTEGER, 
    catch_up_actionable_from_month INTEGER, 
    catch_up_due_at_time VARCHAR, 
    catch_up_due_at_day INTEGER, 
    catch_up_due_at_month INTEGER, 
    birthday VARCHAR, 
    CONSTRAINT pk_person PRIMARY KEY (ref_id), 
    CONSTRAINT fk_person_person_collection_ref_id_person_collection FOREIGN KEY(person_collection_ref_id) REFERENCES person_collection (ref_id)
);""")
    op.execute("""
CREATE INDEX ix_person_person_collection_ref_id ON person (person_collection_ref_id);""")
    op.execute("""
CREATE TABLE person_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    data JSON, kind VARCHAR(16), owner_version INTEGER, source VARCHAR, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES person (ref_id)
);""")
    op.execute("""
CREATE TABLE notion_connection (
    ref_id INTEGER NOT NULL, 
    version INTEGER NOT NULL, 
    archived BOOLEAN NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    archived_time DATETIME, 
    workspace_ref_id INTEGER NOT NULL, 
    space_id VARCHAR NOT NULL, 
    token VARCHAR NOT NULL, 
    PRIMARY KEY (ref_id), 
    FOREIGN KEY(workspace_ref_id) REFERENCES workspace (ref_id)
);""")
    op.execute("""
CREATE UNIQUE INDEX ix_notion_connection_workspace_ref_id ON notion_connection (workspace_ref_id);""")
    op.execute("""
CREATE TABLE notion_connection_event (
    owner_ref_id INTEGER NOT NULL, 
    timestamp DATETIME NOT NULL, 
    session_index INTEGER NOT NULL, 
    name VARCHAR(32) NOT NULL, 
    source VARCHAR(16) NOT NULL, 
    owner_version INTEGER NOT NULL, 
    kind VARCHAR(16) NOT NULL, 
    data JSON, 
    PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
    FOREIGN KEY(owner_ref_id) REFERENCES notion_connection (ref_id)
);""")
    op.execute("""
CREATE TABLE notion_page_link (
    the_key VARCHAR NOT NULL, 
    notion_id VARCHAR NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    PRIMARY KEY (the_key)
);""")
    op.execute("""
CREATE TABLE notion_collection_link (
    the_key VARCHAR NOT NULL, 
    page_notion_id VARCHAR NOT NULL, 
    collection_notion_id VARCHAR NOT NULL, 
    view_notion_ids JSON NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    PRIMARY KEY (the_key)
);""")
    op.execute("""
CREATE TABLE notion_collection_field_tag_link (
    the_key VARCHAR NOT NULL,
    collection_key VARCHAR NOT NULL,
    field VARCHAR NOT NULL,
    ref_id VARCHAR NOT NULL,
    notion_id VARCHAR NOT NULL,
    created_time DATETIME NOT NULL,
    last_modified_time DATETIME NOT NULL,
    PRIMARY KEY (the_key),
    FOREIGN KEY(collection_key) REFERENCES notion_collection_link (the_key)
);""")
    op.execute("""
CREATE INDEX ix_notion_collection_field_tag_link_collection_key ON notion_collection_field_tag_link (collection_key);""")
    op.execute("""
CREATE TABLE notion_collection_item_link (
    the_key VARCHAR NOT NULL, 
    collection_key VARCHAR NOT NULL, 
    ref_id VARCHAR NOT NULL, 
    notion_id VARCHAR NOT NULL, 
    created_time DATETIME NOT NULL, 
    last_modified_time DATETIME NOT NULL, 
    PRIMARY KEY (the_key), 
    FOREIGN KEY(collection_key) REFERENCES notion_collection_link (the_key)
);""")
    op.execute("""
CREATE INDEX ix_notion_collection_item_link_collection_key ON notion_collection_item_link (collection_key);""")


def downgrade() -> None:
    pass
