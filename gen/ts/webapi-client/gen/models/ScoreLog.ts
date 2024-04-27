/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';

/**
 * a log of the scores a user receives.
 */
export type ScoreLog = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    user_ref_id: string;
};

