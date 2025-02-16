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
import type { WorkingMem } from './WorkingMem';

/**
 * A single entry in the load all inbox tasks response.
 */
export type InboxTaskFindResultEntry = {
    inbox_task: InboxTask;
    note?: (Note | null);
    project: Project;
    time_event_blocks?: (Array<TimeEventInDayBlock> | null);
    working_mem?: (WorkingMem | null);
    habit?: (Habit | null);
    chore?: (Chore | null);
    big_plan?: (BigPlan | null);
    metric?: (Metric | null);
    person?: (Person | null);
    slack_task?: (SlackTask | null);
    email_task?: (EmailTask | null);
};

