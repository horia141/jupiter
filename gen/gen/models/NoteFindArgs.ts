/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { NoteSource } from './NoteSource';

export type NoteFindArgs = {
    source: NoteSource;
    allow_archived: boolean;
    include_subnotes: boolean;
    filter_ref_ids?: Array<EntityId>;
};

