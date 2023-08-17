/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';

export type BigPlanCreateArgs = {
    name: EntityName;
    project_ref_id?: EntityId;
    actionable_date?: ADate;
    due_date?: ADate;
};

