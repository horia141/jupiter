/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { PushGenerationExtraInfo } from './PushGenerationExtraInfo';
import type { SlackChannelName } from './SlackChannelName';
import type { SlackUserName } from './SlackUserName';
import type { Timestamp } from './Timestamp';
/**
 * A Slack task which needs to be converted into an inbox task.
 */
export type SlackTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    slack_task_collection_ref_id: string;
    user: SlackUserName;
    message: string;
    generation_extra_info: PushGenerationExtraInfo;
    has_generated_task: boolean;
    channel?: (SlackChannelName | null);
};

