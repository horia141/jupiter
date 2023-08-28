import { ParagraphBlock } from "jupiter-gen";
import { z } from "zod";

export type OneOfNoteContentBlock = ParagraphBlock;

const NoteContentBlockParser = z.discriminatedUnion("kind", [
  z.object({
    kind: z.literal("paragraph").transform(() => ParagraphBlock.kind.PARAGRAPH),
    correlation_id: z.object({
      the_id: z.string(),
    }),
    text: z.string(),
  }),
]);

export const NoteContentParser = z.array(NoteContentBlockParser);
