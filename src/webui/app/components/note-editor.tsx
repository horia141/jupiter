import { TextField } from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { Note } from "jupiter-gen";
import { lazy, Suspense, useEffect, useState } from "react";
import { ClientOnly } from "remix-utils";
import { OneOfNoteContentBlock } from "~/logic/domain/notes";

const BlockEditor = lazy(() => import("~/components/infra/block-editor"));

interface NoteEditorProps {
  initialNote?: Note;
  inputsEnabled: boolean;
}

export function NoteEditor({
  initialNote: note,
  inputsEnabled,
}: NoteEditorProps) {
  const cardActionFetcher = useFetcher();

  const [dataModified, setDataModified] = useState(false);
  const [isActing, setIsActing] = useState(false);
  const [shouldAct, setShouldAct] = useState(false);
  const [noteId, setNoteId] = useState(note ? note.ref_id.the_id : null);
  const [noteName, setNoteName] = useState<string>(
    note ? note.name.the_name : ""
  );
  const [noteContent, setNoteContent] = useState<Array<OneOfNoteContentBlock>>(
    note ? note.content : []
  );

  function act() {
    setIsActing(true);
    if (noteId) {
      // We already created this thing, we just need to update!
      cardActionFetcher.submit(
        {
          id: noteId,
          name: noteName || "Untitled",
          content: btoa(JSON.stringify(noteContent)),
        },
        {
          method: "post",
          action: "/workspace/notes/update",
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
          action: "/workspace/notes/create",
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
  }, [dataModified, noteId, noteName, noteContent]);

  useEffect(() => {
    if (
      cardActionFetcher.submission?.action.endsWith("/create") &&
      cardActionFetcher.data
    ) {
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
