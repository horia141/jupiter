/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { EntityId } from './EntityId';

export type BigPlanCreateArgs = {
    name: BigPlanName;
    project_ref_id?: EntityId;
    actionable_date?: ADate;
    due_date?: ADate;
};

