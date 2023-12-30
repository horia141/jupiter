/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BulletedListBlock } from './BulletedListBlock';
import type { ChecklistBlock } from './ChecklistBlock';
import type { CodeBlock } from './CodeBlock';
import type { DividerBlock } from './DividerBlock';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { EntityReferenceBlock } from './EntityReferenceBlock';
import type { HeadingBlock } from './HeadingBlock';
import type { LinkBlock } from './LinkBlock';
import type { NoteDomain } from './NoteDomain';
import type { NumberedListBlock } from './NumberedListBlock';
import type { ParagraphBlock } from './ParagraphBlock';
import type { ParentLink } from './ParentLink';
import type { QuoteBlock } from './QuoteBlock';
import type { TableBlock } from './TableBlock';
import type { Timestamp } from './Timestamp';

export type Note = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    note_collection: ParentLink;
    domain: NoteDomain;
    source_entity_ref_id: EntityId;
    content: Array<(ParagraphBlock | HeadingBlock | BulletedListBlock | NumberedListBlock | ChecklistBlock | TableBlock | CodeBlock | QuoteBlock | DividerBlock | LinkBlock | EntityReferenceBlock)>;
};

