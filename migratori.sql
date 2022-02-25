insert into chore (
    ref_id, 
	version, 
	archived, 
	created_time, 
	last_modified_time, 
	archived_time, 
	chore_collection_ref_id, 
	project_ref_id, 
	name, 
	gen_params_period, 
	gen_params_eisen, 
	gen_params_difficulty, 
	gen_params_actionable_from_day, 
	gen_params_actionable_from_month, 
	gen_params_due_at_time, 
	gen_params_due_at_day, 
	gen_params_due_at_month, 
	suspended,
	must_do,
	skip_rule, 
	start_at_date, 
	end_at_date
) select ref_id,
	version,
	archived,
	created_time,
	last_modified_time,
	archived_time,
	1 as chore_ref_id,
	project_ref_id,
	name,
	gen_params_period,
	gen_params_eisen,
	gen_params_difficulty,
	gen_params_actionable_from_day,
	gen_params_actionable_from_month,
	gen_params_due_at_time,
	gen_params_due_at_day,
	gen_params_due_at_month,
	suspended,
	must_do,
	skip_rule,
	start_at_date,
	end_at_date
from recurring_task
where the_type = "chore";

insert into chore_event (owner_ref_id, timestamp, session_index, name, source, owner_version, kind, data)
select owner_ref_id, timestamp, session_index, name, source, owner_version, kind, data
from recurring_task_event
where owner_ref_id in (select ref_id from chore);

delete from recurring_task where the_type = "chore";

delete from recurring_task_event where owner_ref_id in (select ref_id from chore);

update inbox_task
set source = "chore", chore_ref_id=recurring_task_ref_id
where recurring_task_ref_id is not null and recurring_task_ref_id in (select ref_id from chore);

update inbox_task
set recurring_task_ref_id=null,recurring_type=null
where source = "chore";