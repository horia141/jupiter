import EditorJS, { OutputData } from "@editorjs/editorjs";
import Header from '@editorjs/header';
import List from '@editorjs/list';
import Checklist from '@editorjs/checklist';
import { ParagraphBlock, HeadingBlock, BulletedListBlock, NumberedListBlock, ChecklistBlock } from "jupiter-gen";
import { useEffect, useRef, useState } from "react";
import { OneOfNoteContentBlock } from "~/logic/domain/notes";

interface BlockEditorProps {
  initialContent: Array<OneOfNoteContentBlock>;
  onChange?: (content: Array<OneOfNoteContentBlock>) => void;
}

export default function BlockEditor(props: BlockEditorProps) {
  const ejInstance = useRef<EditorJS>();

  const initEditor = () => {
    const editor = new EditorJS({
      holder: "editorjs",
      placeholder: "Start writing...",
      autofocus: true,
      data: props.initialContent
        ? transformContentBlocksToEditorJs(props.initialContent)
        : undefined,
      onReady: () => {
        ejInstance.current = editor;
      },
      onChange: async () => {
        const content = await editor.saver.save();

        if (props.onChange) {
          props.onChange(transformEditorJsToContentBlocks(content));
        }
      },
      tools: {
        header: {
          class: Header,
          config: {
            levels: [1, 2, 3],
          }
        },
        list: List,
        checklist: Checklist
      },
    });
  };

  // This will run only once
  useEffect(() => {
    if (!ejInstance.current) {
      initEditor();
    }

    return () => {
      if (ejInstance.current) {
        ejInstance.current.destroy();
      }
      ejInstance.current = undefined;
    };
  }, []);

  return <div id="editorjs"></div>;
}

function transformContentBlocksToEditorJs(
  content: Array<OneOfNoteContentBlock>
): OutputData {
  return {
    time: Date.now(),
    blocks: content.map((block) => {
      switch (block.kind) {
        case ParagraphBlock.kind.PARAGRAPH:
          return {
            type: "paragraph",
            id: block.correlation_id.the_id,
            data: {
              text: block.text,
            },
          };
        case HeadingBlock.kind.HEADING:
          return {
            type: "header",
            id: block.correlation_id.the_id,
            data: {
              text: block.text,
              level: block.level,
            },
          };
        case BulletedListBlock.kind.BULLETED_LIST:
          return {
            type: "list",
            id: block.correlation_id.the_id,
            data: {
              style: "unordered",
              items: block.items,
            }
          };
        case NumberedListBlock.kind.NUMBERED_LIST:
          return {
            type: "list",
            id: block.correlation_id.the_id,
            data: {
              style: "ordered",
              items: block.items,
            }
          };
        case ChecklistBlock.kind.CHECKLIST:
          return {
            type: "checklist",
            id: block.correlation_id.the_id,
            data: {
              items: block.items,
            }
          };
      }
    }),
    version: "2.22.2",
  };
}

function transformEditorJsToContentBlocks(
  content: OutputData
): Array<OneOfNoteContentBlock> {
  return content.blocks.map((block) => {
    switch (block.type) {
      case "paragraph":
        return {
          kind: ParagraphBlock.kind.PARAGRAPH,
          correlation_id: { the_id: block.id as string },
          text: block.data.text as string,
        } as ParagraphBlock;
      case "header":
        return {
          kind: HeadingBlock.kind.HEADING,
          correlation_id: { the_id: block.id as string },
          text: block.data.text as string,
          level: block.data.level as number,
        } as HeadingBlock;
      case "list":
        if (block.data.style === "unordered") {
          return {
            kind: BulletedListBlock.kind.BULLETED_LIST,
            correlation_id: { the_id: block.id as string },
            items: block.data.items as Array<string>,
          } as BulletedListBlock;
        } else if (block.data.style === "ordered") {
          return {
            kind: NumberedListBlock.kind.NUMBERED_LIST,
            correlation_id: { the_id: block.id as string },
            items: block.data.items as Array<string>,
          } as NumberedListBlock;
        } else {
          throw new Error(`Unknown list style: ${block.data.style}`);
        }
      case "checklist":
        return {
          kind: ChecklistBlock.kind.CHECKLIST,
          correlation_id: { the_id: block.id as string },
          items: block.data.items.map((item) => ({
            text: item.text as string,
            checked: item.checked as boolean,
          })) as Array<{ text: string; checked: boolean }>,
        } as ChecklistBlock;
      default:
        throw new Error(`Unknown block type: ${block.type}`);
    }
  });
}
