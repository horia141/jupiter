import { Box } from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { Note } from "jupiter-gen";
import { lazy, Suspense, useEffect, useState } from "react";
import { ClientOnly } from "remix-utils";
import { SomeErrorNoData } from "~/logic/action-result";
import { OneOfNoteContentBlock } from "~/logic/domain/notes";
import { FieldError, GlobalError } from "./infra/errors";

const BlockEditor = lazy(() => import("~/components/infra/block-editor"));

interface EntityNoteEditorProps {
  initialNote: Note;
  inputsEnabled: boolean;
}

export function EntityNoteEditor({
  initialNote,
  inputsEnabled,
}: EntityNoteEditorProps) {
  const cardActionFetcher = useFetcher<SomeErrorNoData>();

  const [dataModified, setDataModified] = useState(false);
  const [isActing, setIsActing] = useState(false);
  const [shouldAct, setShouldAct] = useState(false);
  const [noteContent, setNoteContent] = useState<Array<OneOfNoteContentBlock>>(
    initialNote.content
  );

  function act() {
    setIsActing(true);
    // We already created this thing, we just need to update!
    cardActionFetcher.submit(
      {
        id: initialNote.ref_id.the_id,
        content: btoa(JSON.stringify(noteContent)),
      },
      {
        method: "post",
        action: "/workspace/core/notes/update",
      }
    );
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
  }, [dataModified, noteContent]);

  useEffect(() => {
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
      <GlobalError actionResult={cardActionFetcher.data} />
      <FieldError actionResult={cardActionFetcher.data} fieldName="/content" />

      <ClientOnly fallback={<div>Loading... </div>}>
        {() => (
          <Suspense fallback={<div>Loading...</div>}>
            <Box id="entity-block-editor">
              <BlockEditor
                initialContent={noteContent}
                inputsEnabled={inputsEnabled && !initialNote.archived}
                onChange={(c) => {
                  setDataModified(true);
                  setNoteContent(c);
                }}
              />
            </Box>
          </Suspense>
        )}
      </ClientOnly>
    </>
  );
}
