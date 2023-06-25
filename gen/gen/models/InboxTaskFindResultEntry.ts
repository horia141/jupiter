/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BigPlan } from './BigPlan';
import type { Chore } from './Chore';
import type { EmailTask } from './EmailTask';
import type { Habit } from './Habit';
import type { InboxTask } from './InboxTask';
import type { Metric } from './Metric';
import type { Person } from './Person';
import type { Project } from './Project';
import type { SlackTask } from './SlackTask';

export type InboxTaskFindResultEntry = {
    inbox_task: InboxTask;
    project: Project;
    habit?: Habit;
    chore?: Chore;
    big_plan?: BigPlan;
    metric?: Metric;
    person?: Person;
    slack_task?: SlackTask;
    email_task?: EmailTask;
};

