/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BulletedListBlock } from './BulletedListBlock';
import type { ChecklistBlock } from './ChecklistBlock';
import type { CodeBlock } from './CodeBlock';
import type { DividerBlock } from './DividerBlock';
import type { EntityId } from './EntityId';
import type { EntityReferenceBlock } from './EntityReferenceBlock';
import type { HeadingBlock } from './HeadingBlock';
import type { LinkBlock } from './LinkBlock';
import type { NoteDomain } from './NoteDomain';
import type { NumberedListBlock } from './NumberedListBlock';
import type { ParagraphBlock } from './ParagraphBlock';
import type { QuoteBlock } from './QuoteBlock';
import type { TableBlock } from './TableBlock';
/**
 * NoteCreate args.
 */
export type NoteCreateArgs = {
    domain: NoteDomain;
    source_entity_ref_id: EntityId;
    content: Array<(ParagraphBlock | HeadingBlock | BulletedListBlock | NumberedListBlock | ChecklistBlock | TableBlock | CodeBlock | QuoteBlock | DividerBlock | LinkBlock | EntityReferenceBlock)>;
};

