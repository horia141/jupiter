/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Difficulty } from './Difficulty';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { ScoreSource } from './ScoreSource';
import type { Timestamp } from './Timestamp';

/**
 * A record of a win or loss in accomplishing a task.
 */
export type ScoreLogEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    score_log_ref_id: string;
    source: ScoreSource;
    task_ref_id: EntityId;
    difficulty: Difficulty;
    success: boolean;
    has_lucky_puppy_bonus?: (boolean | null);
    score: number;
};

