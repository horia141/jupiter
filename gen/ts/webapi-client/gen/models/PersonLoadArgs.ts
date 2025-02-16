/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * PersonLoadArgs.
 */
export type PersonLoadArgs = {
    ref_id: EntityId;
    allow_archived: boolean;
    catch_up_task_retrieve_offset?: (number | null);
    birthday_task_retrieve_offset?: (number | null);
};

