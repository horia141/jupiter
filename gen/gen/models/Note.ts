/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { NoteContentBlock } from './NoteContentBlock';
import type { NoteSource } from './NoteSource';
import type { Timestamp } from './Timestamp';

export type Note = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    note_collection_ref_id: EntityId;
    parent_note_ref_id: EntityId;
    source: NoteSource;
    source_entity_ref_id: EntityId;
    content: Array<NoteContentBlock>;
};

