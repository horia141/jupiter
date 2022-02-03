update big_plan
set project_ref_id =
 (select rtc.project_ref_id
  from big_plan_collection as rtc
  where big_plan.big_plan_collection_ref_id = rtc.ref_id)
where project_ref_id is null