/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { BigPlanStatus } from './BigPlanStatus';
import type { EntityId } from './EntityId';
import type { ParentLink } from './ParentLink';
import type { Timestamp } from './Timestamp';

export type BigPlan = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: BigPlanName;
    big_plan_collection: ParentLink;
    project_ref_id: EntityId;
    status: BigPlanStatus;
    actionable_date?: ADate;
    due_date?: ADate;
    accepted_time?: Timestamp;
    working_time?: Timestamp;
    completed_time?: Timestamp;
};

