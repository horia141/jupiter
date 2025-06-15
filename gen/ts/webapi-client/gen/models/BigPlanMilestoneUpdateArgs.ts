/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
/**
 * Big plan milestone update args.
 */
export type BigPlanMilestoneUpdateArgs = {
    ref_id: EntityId;
    date: {
        should_change: boolean;
        value?: ADate;
    };
    name: {
        should_change: boolean;
        value?: EntityName;
    };
};

