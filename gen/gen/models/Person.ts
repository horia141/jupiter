/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { PersonBirthday } from './PersonBirthday';
import type { PersonName } from './PersonName';
import type { PersonRelationship } from './PersonRelationship';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { Timestamp } from './Timestamp';

export type Person = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: PersonName;
    person_collection_ref_id: EntityId;
    relationship: PersonRelationship;
    catch_up_params?: RecurringTaskGenParams;
    birthday?: PersonBirthday;
};

