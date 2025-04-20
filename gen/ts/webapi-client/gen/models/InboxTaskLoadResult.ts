/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlan } from './BigPlan';
import type { Chore } from './Chore';
import type { EmailTask } from './EmailTask';
import type { Habit } from './Habit';
import type { InboxTask } from './InboxTask';
import type { Metric } from './Metric';
import type { Note } from './Note';
import type { Person } from './Person';
import type { Project } from './Project';
import type { SlackTask } from './SlackTask';
import type { TimeEventInDayBlock } from './TimeEventInDayBlock';
import type { TimePlan } from './TimePlan';
import type { WorkingMem } from './WorkingMem';
/**
 * InboxTaskLoadResult.
 */
export type InboxTaskLoadResult = {
    inbox_task: InboxTask;
    project: Project;
    working_mem?: (WorkingMem | null);
    time_plan?: (TimePlan | null);
    habit?: (Habit | null);
    chore?: (Chore | null);
    big_plan?: (BigPlan | null);
    metric?: (Metric | null);
    person?: (Person | null);
    slack_task?: (SlackTask | null);
    email_task?: (EmailTask | null);
    note?: (Note | null);
    time_event_blocks: Array<TimeEventInDayBlock>;
};

