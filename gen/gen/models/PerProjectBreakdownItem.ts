/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { InboxTasksSummary } from './InboxTasksSummary';
import type { WorkableSummary } from './WorkableSummary';

export type PerProjectBreakdownItem = {
    ref_id: EntityId;
    name: EntityName;
    inbox_tasks_summary: InboxTasksSummary;
    big_plans_summary: WorkableSummary;
};
