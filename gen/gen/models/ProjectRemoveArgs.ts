/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Project remove args.
 */
export type ProjectRemoveArgs = {
    ref_id: EntityId;
    backup_project_ref_id?: EntityId;
};

