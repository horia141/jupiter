/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmailAddress } from './EmailAddress';
import type { EmailUserName } from './EmailUserName';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { PushGenerationExtraInfo } from './PushGenerationExtraInfo';
import type { Timestamp } from './Timestamp';
/**
 * An email task which needs to be converted into an inbox task.
 */
export type EmailTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    email_task_collection_ref_id: string;
    from_address: EmailAddress;
    from_name: EmailUserName;
    to_address: EmailAddress;
    subject: string;
    body: string;
    generation_extra_info: PushGenerationExtraInfo;
    has_generated_task: boolean;
};

