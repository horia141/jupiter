/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';
import type { WorkspaceName } from './WorkspaceName';

export type Workspace = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: WorkspaceName;
    default_project_ref_id: EntityId;
    feature_flags: Record<string, boolean>;
};

