/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';
import type { WorkspaceName } from './WorkspaceName';

/**
 * The workspace where everything happens.
 */
export type Workspace = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    name: WorkspaceName;
    feature_flags: Record<string, boolean>;
};

