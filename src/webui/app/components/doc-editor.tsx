import { TextField } from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { Doc, Note } from "jupiter-gen";
import { lazy, Suspense, useEffect, useState } from "react";
import { ClientOnly } from "remix-utils";
import { OneOfNoteContentBlock } from "~/logic/domain/notes";

const BlockEditor = lazy(() => import("~/components/infra/block-editor"));

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
  const cardActionFetcher = useFetcher();

  const [dataModified, setDataModified] = useState(false);
  const [isActing, setIsActing] = useState(false);
  const [shouldAct, setShouldAct] = useState(false);
  const [docId, setDocId] = useState(initialDoc ? initialDoc.ref_id.the_id : null);
  const [noteId, setNoteId] = useState(initialNote ? initialNote.ref_id.the_id : null)
  const [noteName, setNoteName] = useState<string>(
    initialDoc ? initialDoc.name.the_name : ""
  );
  const [noteContent, setNoteContent] = useState<Array<OneOfNoteContentBlock>>(
    initialNote ? initialNote.content : []
  );

  function act() {
    setIsActing(true);
    if (docId) {
      // We already created this thing, we just need to update!
      cardActionFetcher.submit(
        {
          docId: docId,
          noteId: noteId,
          name: noteName || "Untitled",
          content: btoa(JSON.stringify(noteContent)),
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
          content: btoa(JSON.stringify(noteContent)),
        },
        {
          method: "post",
          action: "/workspace/docs/create-action",
        }
      );
    }
    setDataModified(false);
  }

  useEffect(() => {
    if (dataModified) {
      if (!isActing) {
        act();
      } else {
        setShouldAct(true);
      }
    }
  }, [dataModified, docId, noteId, noteName, noteContent]);

  useEffect(() => {
    if (
      cardActionFetcher.submission?.action.endsWith("/create-action") &&
      cardActionFetcher.data
    ) {
      setDocId(cardActionFetcher.data?.data.new_doc.ref_id.the_id);
      setNoteId(cardActionFetcher.data?.data.new_note.ref_id.the_id);
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
  }, [cardActionFetcher]);

  return (
    <>
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
