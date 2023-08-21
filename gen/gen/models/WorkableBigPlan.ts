/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';

export type WorkableBigPlan = {
    ref_id: EntityId;
    name: EntityName;
    actionable_date?: ADate;
};

