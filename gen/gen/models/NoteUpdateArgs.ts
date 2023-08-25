/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { NoteContentBlock } from './NoteContentBlock';

export type NoteUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: EntityName;
    };
    content: {
        should_change: boolean;
        value?: Array<NoteContentBlock>;
    };
};

