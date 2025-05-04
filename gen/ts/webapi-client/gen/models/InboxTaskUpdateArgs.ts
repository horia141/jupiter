/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { InboxTaskName } from './InboxTaskName';
import type { InboxTaskStatus } from './InboxTaskStatus';
/**
 * PersonFindArgs.
 */
export type InboxTaskUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: InboxTaskName;
    };
    status: {
        should_change: boolean;
        value?: InboxTaskStatus;
    };
    project_ref_id: {
        should_change: boolean;
        value?: EntityId;
    };
    big_plan_ref_id: {
        should_change: boolean;
        value?: (EntityId | null);
    };
    is_key: {
        should_change: boolean;
        value?: boolean;
    };
    eisen: {
        should_change: boolean;
        value?: Eisen;
    };
    difficulty: {
        should_change: boolean;
        value?: Difficulty;
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

