/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BulletedListBlock } from './BulletedListBlock';
import type { ChecklistBlock } from './ChecklistBlock';
import type { CodeBlock } from './CodeBlock';
import type { DividerBlock } from './DividerBlock';
import type { DocName } from './DocName';
import type { EntityId } from './EntityId';
import type { EntityReferenceBlock } from './EntityReferenceBlock';
import type { HeadingBlock } from './HeadingBlock';
import type { LinkBlock } from './LinkBlock';
import type { NumberedListBlock } from './NumberedListBlock';
import type { ParagraphBlock } from './ParagraphBlock';
import type { QuoteBlock } from './QuoteBlock';
import type { TableBlock } from './TableBlock';

/**
 * DocCreate args.
 */
export type DocCreateArgs = {
    name: DocName;
    content: Array<(ParagraphBlock | HeadingBlock | BulletedListBlock | NumberedListBlock | ChecklistBlock | TableBlock | CodeBlock | QuoteBlock | DividerBlock | LinkBlock | EntityReferenceBlock)>;
    parent_doc_ref_id?: (EntityId | null);
};

