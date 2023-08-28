/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BulletedListBlock } from './BulletedListBlock';
import type { ChecklistBlock } from './ChecklistBlock';
import type { DividerBlock } from './DividerBlock';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { EntityReferenceBlock } from './EntityReferenceBlock';
import type { HeadingBlock } from './HeadingBlock';
import type { LinkBlock } from './LinkBlock';
import type { NumberedListBlock } from './NumberedListBlock';
import type { ParagraphBlock } from './ParagraphBlock';
import type { QuoteBlock } from './QuoteBlock';

export type NoteCreateArgs = {
    name: EntityName;
    content: Array<(ParagraphBlock | HeadingBlock | BulletedListBlock | NumberedListBlock | ChecklistBlock | QuoteBlock | DividerBlock | LinkBlock | EntityReferenceBlock)>;
    parent_note_ref_id?: EntityId;
};

