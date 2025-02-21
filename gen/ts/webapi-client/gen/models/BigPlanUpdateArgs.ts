/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { BigPlanStatus } from './BigPlanStatus';
import type { EntityId } from './EntityId';

/**
 * PersonFindArgs.
 */
export type BigPlanUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: BigPlanName;
    };
    status: {
        should_change: boolean;
        value?: BigPlanStatus;
    };
    project_ref_id: {
        should_change: boolean;
        value?: EntityId;
    };
    actionable_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
    due_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
};

