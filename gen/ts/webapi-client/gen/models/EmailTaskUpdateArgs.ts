/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EmailAddress } from './EmailAddress';
import type { EmailUserName } from './EmailUserName';
import type { EntityId } from './EntityId';
import type { InboxTaskName } from './InboxTaskName';
import type { InboxTaskStatus } from './InboxTaskStatus';
/**
 * PersonFindArgs.
 */
export type EmailTaskUpdateArgs = {
    ref_id: EntityId;
    from_address: {
        should_change: boolean;
        value?: EmailAddress;
    };
    from_name: {
        should_change: boolean;
        value?: EmailUserName;
    };
    to_address: {
        should_change: boolean;
        value?: EmailAddress;
    };
    subject: {
        should_change: boolean;
        value?: string;
    };
    body: {
        should_change: boolean;
        value?: string;
    };
    generation_name: {
        should_change: boolean;
        value?: (InboxTaskName | null);
    };
    generation_status: {
        should_change: boolean;
        value?: (InboxTaskStatus | null);
    };
    generation_eisen: {
        should_change: boolean;
        value?: Eisen;
    };
    generation_difficulty: {
        should_change: boolean;
        value?: Difficulty;
    };
    generation_actionable_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
    generation_due_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
};

