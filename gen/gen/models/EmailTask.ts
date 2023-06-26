/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailAddress } from './EmailAddress';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { PushGenerationExtraInfo } from './PushGenerationExtraInfo';
import type { Timestamp } from './Timestamp';

export type EmailTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    email_task_collection_ref_id: EntityId;
    from_address: EmailAddress;
    from_name: EntityName;
    to_address: EmailAddress;
    subject: string;
    body: string;
    generation_extra_info: PushGenerationExtraInfo;
    has_generated_task: boolean;
};
