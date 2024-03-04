import editorjsCodeflask from "@calumk/editorjs-codeflask";
import Checklist from "@editorjs/checklist";
import Delimiter from "@editorjs/delimiter";
import type { OutputData } from "@editorjs/editorjs";
import EditorJS from "@editorjs/editorjs";
import Header from "@editorjs/header";
import NestedList from "@editorjs/nested-list";
import Quote from "@editorjs/quote";
import Table from "@editorjs/table";
import DragDrop from "editorjs-drag-drop";
import type { ListItem } from "jupiter-gen";
import {
  BulletedListBlock,
  ChecklistBlock,
  CodeBlock,
  DividerBlock,
  EntityReferenceBlock,
  HeadingBlock,
  LinkBlock,
  NumberedListBlock,
  ParagraphBlock,
  QuoteBlock,
  TableBlock,
} from "jupiter-gen";
import { useEffect, useRef } from "react";
import type { OneOfNoteContentBlock } from "~/logic/domain/notes";

export interface BlockEditorProps {
  initialContent: Array<OneOfNoteContentBlock>;
  inputsEnabled: boolean;
  onChange?: (content: Array<OneOfNoteContentBlock>) => void;
}

export default function BlockEditor(props: BlockEditorProps) {
  const ejInstance = useRef<EditorJS>();

  const initEditor = () => {
    const editor = new EditorJS({
      holder: "editorjs",
      placeholder: "Start writing...",
      autofocus: true,
      readOnly: !props.inputsEnabled,
      data: props.initialContent
        ? transformContentBlocksToEditorJs(props.initialContent)
        : undefined,
      onReady: () => {
        ejInstance.current = editor;
        new DragDrop(editor);
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
          inlineToolbar: true,
          config: {
            levels: [1, 2, 3],
          },
        },
        list: {
          class: NestedList,
          inlineToolbar: true,
        },
        checklist: {
          class: Checklist,
          inlineToolbar: true,
        },
        table: {
          class: Table,
          inlineToolbar: true,
          config: {
            rows: 2,
            cols: 3,
          },
        },
        code: editorjsCodeflask,
        quote: {
          class: Quote,
          inlineToolbar: true,
        },
        delimiter: Delimiter,
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <div id="editorjs"></div>;
}

type EditorJsListItem = {
  content: string;
  items: Array<EditorJsListItem>;
};

function transformContentBlocksToEditorJs(
  content: Array<OneOfNoteContentBlock>
): OutputData {
  function transformListItemToEditorJs(listItem: ListItem): EditorJsListItem {
    return {
      content: listItem.text,
      items: listItem.items.map(transformListItemToEditorJs),
    };
  }

  return {
    time: Date.now(),
    blocks: content.map((block) => {
      switch (block.kind) {
        case ParagraphBlock.kind.PARAGRAPH:
          return {
            type: "paragraph",
            id: block.correlation_id,
            data: {
              text: block.text,
            },
          };
        case HeadingBlock.kind.HEADING:
          return {
            type: "header",
            id: block.correlation_id,
            data: {
              text: block.text,
              level: block.level,
            },
          };
        case BulletedListBlock.kind.BULLETED_LIST:
          return {
            type: "list",
            id: block.correlation_id,
            data: {
              style: "unordered",
              items: block.items.map(transformListItemToEditorJs),
            },
          };
        case NumberedListBlock.kind.NUMBERED_LIST:
          return {
            type: "list",
            id: block.correlation_id,
            data: {
              style: "ordered",
              items: block.items.map(transformListItemToEditorJs),
            },
          };
        case ChecklistBlock.kind.CHECKLIST:
          return {
            type: "checklist",
            id: block.correlation_id,
            data: {
              items: block.items,
            },
          };
        case TableBlock.kind.TABLE:
          return {
            type: "table",
            id: block.correlation_id,
            data: {
              withHeadings: block.with_header,
              content: block.contents,
            },
          };
        case CodeBlock.kind.CODE:
          return {
            type: "code",
            id: block.correlation_id,
            data: {
              code: block.code,
              language: block.language,
              showlinenumbers: block.show_line_numbers,
            },
          };
        case QuoteBlock.kind.QUOTE:
          return {
            type: "quote",
            id: block.correlation_id,
            data: {
              text: block.text,
              caption: "",
            },
          };
        case DividerBlock.kind.DIVIDER:
          return {
            type: "delimiter",
            id: block.correlation_id,
            data: {},
          };
        case LinkBlock.kind.LINK:
          throw new Error("Link blocks are not supported right now");
        case EntityReferenceBlock.kind.ENTITY_REFERENCE:
          throw new Error(
            "Entity reference blocks are not supported right now"
          );
        default:
          throw new Error(`Unknown block kind: ${block}`);
      }
    }),
    version: "2.22.2",
  };
}

function transformEditorJsToContentBlocks(
  content: OutputData
): Array<OneOfNoteContentBlock> {
  function transformEditorJsToListItem(listItem: EditorJsListItem): ListItem {
    return {
      text: listItem.content,
      items: listItem.items.map(transformEditorJsToListItem),
    };
  }

  return content.blocks.map((block) => {
    switch (block.type) {
      case "paragraph":
        return {
          kind: ParagraphBlock.kind.PARAGRAPH,
          correlation_id: block.id as string,
          text: block.data.text as string,
        } as ParagraphBlock;
      case "header":
        return {
          kind: HeadingBlock.kind.HEADING,
          correlation_id: block.id as string,
          text: block.data.text as string,
          level: block.data.level as number,
        } as HeadingBlock;
      case "list":
        if (block.data.style === "unordered") {
          return {
            kind: BulletedListBlock.kind.BULLETED_LIST,
            correlation_id: block.id as string,
            items: block.data.items.map(transformEditorJsToListItem),
          } as BulletedListBlock;
        } else if (block.data.style === "ordered") {
          return {
            kind: NumberedListBlock.kind.NUMBERED_LIST,
            correlation_id: block.id as string,
            items: block.data.items.map(transformEditorJsToListItem),
          } as NumberedListBlock;
        } else {
          throw new Error(`Unknown list style: ${block.data.style}`);
        }
      case "checklist":
        return {
          kind: ChecklistBlock.kind.CHECKLIST,
          correlation_id: block.id as string,
          items: block.data.items.map(
            (item: { text: string; checked: boolean }) => ({
              text: item.text,
              checked: item.checked,
            })
          ),
        } as ChecklistBlock;
      case "table":
        return {
          kind: TableBlock.kind.TABLE,
          correlation_id: block.id as string,
          with_header: block.data.withHeadings as boolean,
          contents: block.data.content as Array<Array<string>>,
        } as TableBlock;
      case "code":
        return {
          kind: CodeBlock.kind.CODE,
          correlation_id: block.id as string,
          code: block.data.code as string,
          language: block.data.language as string | undefined,
          show_line_numbers: block.data.showlinenumbers as boolean | undefined,
        } as CodeBlock;
      case "quote":
        return {
          kind: QuoteBlock.kind.QUOTE,
          correlation_id: block.id as string,
          text: block.data.text as string,
        } as QuoteBlock;
      case "delimiter":
        return {
          kind: DividerBlock.kind.DIVIDER,
          correlation_id: block.id as string,
        } as DividerBlock;
      default:
        throw new Error(`Unknown block type: ${block.type}`);
    }
  });
}
