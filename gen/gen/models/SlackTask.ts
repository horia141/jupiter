/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { PushGenerationExtraInfo } from './PushGenerationExtraInfo';
import type { SlackChannelName } from './SlackChannelName';
import type { Timestamp } from './Timestamp';

export type SlackTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    slack_task_collection_ref_id: EntityId;
    user: EntityName;
    message: string;
    generation_extra_info: PushGenerationExtraInfo;
    has_generated_task: boolean;
    channel?: SlackChannelName;
};

