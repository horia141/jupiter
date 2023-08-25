/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { NoteContentBlock } from './NoteContentBlock';

export type NoteCreateArgs = {
    parent_note_ref_id: EntityId;
    name: EntityName;
    content: Array<NoteContentBlock>;
};

