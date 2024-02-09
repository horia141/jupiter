/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { ParentLink } from './ParentLink';
import type { PushGenerationExtraInfo } from './PushGenerationExtraInfo';
import type { SlackChannelName } from './SlackChannelName';
import type { SlackUserName } from './SlackUserName';
import type { Timestamp } from './Timestamp';
export type SlackTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    slack_task_collection: ParentLink;
    user: SlackUserName;
    message: string;
    generation_extra_info: PushGenerationExtraInfo;
    has_generated_task: boolean;
    channel?: SlackChannelName;
};

