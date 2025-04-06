/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { Person } from './Person';
import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';
/**
 * PersonLoadResult.
 */
export type PersonLoadResult = {
    person: Person;
    birthday_time_event_blocks: Array<TimeEventFullDaysBlock>;
    catch_up_tasks: Array<InboxTask>;
    catch_up_tasks_total_cnt: number;
    catch_up_tasks_page_size: number;
    birthday_tasks: Array<InboxTask>;
    birthday_tasks_total_cnt: number;
    birthday_tasks_page_size: number;
    note?: (Note | null);
};

