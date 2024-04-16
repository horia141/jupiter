/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';

/**
 * A 1:1 link between a user and a workspace.
 */
export type UserWorkspaceLink = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    user_ref_id: EntityId;
    workspace_ref_id: EntityId;
};

