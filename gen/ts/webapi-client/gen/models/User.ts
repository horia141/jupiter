/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Avatar } from './Avatar';
import type { EmailAddress } from './EmailAddress';
import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';
import type { Timezone } from './Timezone';
import type { UserName } from './UserName';

/**
 * A user of jupiter.
 */
export type User = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    email_address: EmailAddress;
    name: UserName;
    avatar: Avatar;
    timezone: Timezone;
    feature_flags: Record<string, boolean>;
};

