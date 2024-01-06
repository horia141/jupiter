/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Avatar } from './Avatar';
import type { EmailAddress } from './EmailAddress';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { Timestamp } from './Timestamp';
import type { Timezone } from './Timezone';

export type User = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    email_address: EmailAddress;
    name: EntityName;
    avatar: Avatar;
    timezone: Timezone;
    feature_flags: Record<string, boolean>;
};

