/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';
import type { Timestamp } from './Timestamp';

export type Habit = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    habit_collection_ref_id: EntityId;
    project_ref_id: EntityId;
    gen_params: RecurringTaskGenParams;
    skip_rule?: RecurringTaskSkipRule;
    suspended?: boolean;
    repeats_in_period_count?: number;
};

