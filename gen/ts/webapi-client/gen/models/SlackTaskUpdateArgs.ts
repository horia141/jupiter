/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { InboxTaskName } from './InboxTaskName';
import type { InboxTaskStatus } from './InboxTaskStatus';
import type { SlackChannelName } from './SlackChannelName';
import type { SlackUserName } from './SlackUserName';

/**
 * PersonFindArgs.
 */
export type SlackTaskUpdateArgs = {
    ref_id: EntityId;
    user: {
        should_change: boolean;
        value?: SlackUserName;
    };
    channel: {
        should_change: boolean;
        value?: (SlackChannelName | null);
    };
    message: {
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
        value?: (Eisen | null);
    };
    generation_difficulty: {
        should_change: boolean;
        value?: (Difficulty | null);
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

