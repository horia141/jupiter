/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { BigPlanStatus } from './BigPlanStatus';
import type { EntityId } from './EntityId';
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
    actionable_date: {
        should_change: boolean;
        value?: ADate;
    };
    due_date: {
        should_change: boolean;
        value?: ADate;
    };
};

