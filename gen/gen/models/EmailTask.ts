/* generated using openapi-typescript-codegen -- do no edit */
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
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    name: EntityName;
    email_task_collection: string;
    from_address: EmailAddress;
    from_name: EmailUserName;
    to_address: EmailAddress;
    subject: string;
    body: string;
    generation_extra_info: PushGenerationExtraInfo;
    has_generated_task: boolean;
};

