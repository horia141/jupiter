import {
  BulletedListBlock,
  ChecklistBlock,
  CodeBlock,
  DividerBlock,
  HeadingBlock,
  NumberedListBlock,
  ParagraphBlock,
  QuoteBlock,
  TableBlock,
} from "jupiter-gen";
import { z } from "zod";

export type OneOfNoteContentBlock =
  | ParagraphBlock
  | HeadingBlock
  | BulletedListBlock
  | NumberedListBlock
  | ChecklistBlock
  | TableBlock
  | CodeBlock
  | QuoteBlock
  | DividerBlock;

const BASE_LIST_ITEM_SCHEMA = z.object({
  text: z.string(),
});

type ListItem = z.infer<typeof BASE_LIST_ITEM_SCHEMA> & {
  items: Array<ListItem>;
};

const LIST_ITEM_SCHEMA: z.ZodType<ListItem> = BASE_LIST_ITEM_SCHEMA.extend({
  items: z.lazy(() => z.array(LIST_ITEM_SCHEMA)),
});

const NOTE_CONTENT_BLOCK_PARSER = z.discriminatedUnion("kind", [
  z.object({
    kind: z.literal("paragraph").transform(() => ParagraphBlock.kind.PARAGRAPH),
    correlation_id: z.string(),
    text: z.string(),
  }),
  z.object({
    kind: z.literal("heading").transform(() => HeadingBlock.kind.HEADING),
    correlation_id: z.string(),
    text: z.string(),
    level: z.number(),
  }),
  z.object({
    kind: z
      .literal("bulleted-list")
      .transform(() => BulletedListBlock.kind.BULLETED_LIST),
    correlation_id: z.string(),
    items: z.array(LIST_ITEM_SCHEMA),
  }),
  z.object({
    kind: z
      .literal("numbered-list")
      .transform(() => NumberedListBlock.kind.NUMBERED_LIST),
    correlation_id: z.string(),
    items: z.array(LIST_ITEM_SCHEMA),
  }),
  z.object({
    kind: z.literal("checklist").transform(() => ChecklistBlock.kind.CHECKLIST),
    correlation_id: z.string(),
    items: z.array(
      z.object({
        text: z.string(),
        checked: z.boolean(),
      })
    ),
  }),
  z.object({
    kind: z.literal("table").transform(() => TableBlock.kind.TABLE),
    correlation_id: z.string(),
    with_header: z.boolean(),
    contents: z.array(z.array(z.string())),
  }),
  z.object({
    kind: z.literal("code").transform(() => CodeBlock.kind.CODE),
    correlation_id: z.string(),
    code: z.string(),
    language: z.string().optional(),
    show_line_numbers: z.boolean().optional(),
  }),
  z.object({
    kind: z.literal("quote").transform(() => QuoteBlock.kind.QUOTE),
    correlation_id: z.string(),
    text: z.string(),
  }),
  z.object({
    kind: z.literal("divider").transform(() => DividerBlock.kind.DIVIDER),
    correlation_id: z.string(),
  }),
]);

export const NoteContentParser = z.array(NOTE_CONTENT_BLOCK_PARSER);
