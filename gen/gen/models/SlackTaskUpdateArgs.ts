/* generated using openapi-typescript-codegen -- do no edit */
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
export type SlackTaskUpdateArgs = {
    ref_id: EntityId;
    user: {
        should_change: boolean;
        value?: SlackUserName;
    };
    channel: {
        should_change: boolean;
        value?: SlackChannelName;
    };
    message: {
        should_change: boolean;
        value?: string;
    };
    generation_name: {
        should_change: boolean;
        value?: InboxTaskName;
    };
    generation_status: {
        should_change: boolean;
        value?: InboxTaskStatus;
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
        value?: ADate;
    };
    generation_due_date: {
        should_change: boolean;
        value?: ADate;
    };
};

