import EditorJS, { OutputData } from "@editorjs/editorjs";
import { ParagraphBlock } from "jupiter-gen";
import { useEffect, useRef } from "react";
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
        // header: Header,
        // list: List,
        // checklist: Checklist
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
        default:
          throw new Error(`Unknown block kind: ${block.kind}`);
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
      default:
        throw new Error(`Unknown block type: ${block.type}`);
    }
  });
}
