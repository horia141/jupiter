/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';
import type { Timestamp } from './Timestamp';

export type Chore = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    chore_collection_ref_id: EntityId;
    project_ref_id: EntityId;
    gen_params: RecurringTaskGenParams;
    suspended: boolean;
    must_do: boolean;
    start_at_date: ADate;
    end_at_date?: ADate;
    skip_rule?: RecurringTaskSkipRule;
};

