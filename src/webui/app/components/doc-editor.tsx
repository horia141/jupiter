import { TextField } from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { Buffer } from "buffer-polyfill";
import type { Doc, DocCreateResult, Note } from "jupiter-gen";
import type { ComponentType } from "react";
import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { ClientOnly } from "remix-utils";
import type { NoErrorSomeData, SomeErrorNoData } from "~/logic/action-result";
import { isNoErrorSomeData } from "~/logic/action-result";
import type { OneOfNoteContentBlock } from "~/logic/domain/notes";
import type { BlockEditorProps } from "./infra/block-editor";
import { FieldError, GlobalError } from "./infra/errors";

const BlockEditor = lazy(() =>
  import("~/components/infra/block-editor.js").then((module) => ({
    default: module.default as unknown as ComponentType<BlockEditorProps>,
  }))
);

interface DocEditorProps {
  initialDoc?: Doc;
  initialNote?: Note;
  inputsEnabled: boolean;
}

export function DocEditor({
  initialDoc,
  initialNote,
  inputsEnabled,
}: DocEditorProps) {
  const cardActionFetcher = useFetcher<
    SomeErrorNoData | NoErrorSomeData<DocCreateResult>
  >();

  const [dataModified, setDataModified] = useState(false);
  const [isActing, setIsActing] = useState(false);
  const [shouldAct, setShouldAct] = useState(false);
  const [docId, setDocId] = useState(initialDoc ? initialDoc.ref_id : null);
  const [noteId, setNoteId] = useState(initialNote ? initialNote.ref_id : null);
  const [noteName, setNoteName] = useState<string>(
    initialDoc ? initialDoc.name : ""
  );
  const [noteContent, setNoteContent] = useState<Array<OneOfNoteContentBlock>>(
    initialNote ? initialNote.content : []
  );

  const act = useCallback(() => {
    setIsActing(true);
    const base64Content = Buffer.from(
      JSON.stringify(noteContent),
      "utf-8"
    ).toString("base64");
    if (docId && noteId) {
      // We already created this thing, we just need to update!
      cardActionFetcher.submit(
        {
          docId: docId,
          noteId: noteId,
          name: noteName || "Untitled",
          content: base64Content,
        },
        {
          method: "post",
          action: "/workspace/docs/update-action",
        }
      );
    } else {
      // We need to create it!
      cardActionFetcher.submit(
        {
          name: noteName || "Untitled",
          content: base64Content,
        },
        {
          method: "post",
          action: "/workspace/docs/create-action",
        }
      );
    }
    setDataModified(false);
  }, [cardActionFetcher, docId, noteContent, noteId, noteName]);

  useEffect(() => {
    if (dataModified) {
      if (!isActing) {
        act();
      } else {
        setShouldAct(true);
      }
    }
  }, [dataModified, docId, noteId, noteName, noteContent, isActing, act]);

  useEffect(() => {
    if (
      cardActionFetcher.submission?.action.endsWith("/create-action") &&
      cardActionFetcher.data &&
      isNoErrorSomeData(cardActionFetcher.data)
    ) {
      setDocId(cardActionFetcher.data?.data.new_doc.ref_id);
      setNoteId(cardActionFetcher.data?.data.new_note.ref_id);
    }

    if (
      cardActionFetcher.state === "idle" &&
      cardActionFetcher.type === "done"
    ) {
      setIsActing(false);
      if (shouldAct) {
        act();
        setShouldAct(false);
      }
    }
  }, [cardActionFetcher, act, shouldAct]);

  return (
    <>
      <GlobalError actionResult={cardActionFetcher.data} />

      <TextField
        label="Name"
        name="name"
        variant="standard"
        InputProps={{
          readOnly: !inputsEnabled,
        }}
        defaultValue={noteName}
        onChange={(e) => {
          setDataModified(true);
          setNoteName(e.target.value);
        }}
      />
      <FieldError actionResult={cardActionFetcher.data} fieldName="/name" />
      <FieldError actionResult={cardActionFetcher.data} fieldName="/content" />

      <ClientOnly fallback={<div>Loading... </div>}>
        {() => (
          <Suspense fallback={<div>Loading...</div>}>
            <BlockEditor
              initialContent={noteContent}
              inputsEnabled={inputsEnabled}
              onChange={(c) => {
                setDataModified(true);
                setNoteContent(c);
              }}
            />
          </Suspense>
        )}
      </ClientOnly>
    </>
  );
}
