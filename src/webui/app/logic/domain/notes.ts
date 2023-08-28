import { BulletedListBlock, ChecklistBlock, HeadingBlock, NumberedListBlock, ParagraphBlock } from "jupiter-gen";
import { z } from "zod";

export type OneOfNoteContentBlock = ParagraphBlock | HeadingBlock | BulletedListBlock | NumberedListBlock | ChecklistBlock;

const NoteContentBlockParser = z.discriminatedUnion("kind", [
  z.object({
    kind: z.literal("paragraph").transform(() => ParagraphBlock.kind.PARAGRAPH),
    correlation_id: z.object({
      the_id: z.string(),
    }),
    text: z.string(),
  }),
  z.object({
    kind: z.literal("heading").transform(() => HeadingBlock.kind.HEADING),
    correlation_id: z.object({
      the_id: z.string(),
    }),
    text: z.string(),
    level: z.number(),
  }),
  z.object({
    kind: z.literal("bulleted-list").transform(() => BulletedListBlock.kind.BULLETED_LIST),
    correlation_id: z.object({
      the_id: z.string(),
    }),
    items: z.array(z.string()),
  }),
  z.object({
    kind: z.literal("numbered-list").transform(() => NumberedListBlock.kind.NUMBERED_LIST),
    correlation_id: z.object({
      the_id: z.string(),
    }),
    items: z.array(z.string()),
  }),
  z.object({
    kind: z.literal("checklist").transform(() => ChecklistBlock.kind.CHECKLIST),
    correlation_id: z.object({
      the_id: z.string(),
    }),
    items: z.array(z.object({
      text: z.string(),
      checked: z.boolean(),
    })),
  }),
]);

export const NoteContentParser = z.array(NoteContentBlockParser);
