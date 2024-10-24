import type { Note } from "@jupiter/webapi-client";
import { Box } from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { Buffer } from "buffer-polyfill";
import type { ComponentType } from "react";
import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { ClientOnly } from "remix-utils";
import type { SomeErrorNoData } from "~/logic/action-result";
import type { OneOfNoteContentBlock } from "~/logic/domain/notes";
import type { BlockEditorProps } from "./infra/block-editor";
import { FieldError, GlobalError } from "./infra/errors";

const BlockEditor = lazy(() =>
  import("~/components/infra/block-editor.js").then((module) => ({
    default: module.default as unknown as ComponentType<BlockEditorProps>,
  }))
);

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

  const act = useCallback(() => {
    setIsActing(true);
    const base64Content = Buffer.from(
      JSON.stringify(noteContent),
      "utf-8"
    ).toString("base64");
    // We already created this thing, we just need to update!
    cardActionFetcher.submit(
      {
        id: initialNote.ref_id,
        content: base64Content,
      },
      {
        method: "post",
        action: "/workspace/core/notes/update",
      }
    );
    setDataModified(false);
  }, [cardActionFetcher, initialNote.ref_id, noteContent]);

  useEffect(() => {
    if (dataModified) {
      if (!isActing) {
        act();
      } else {
        setShouldAct(true);
      }
    }
  }, [act, dataModified, isActing, noteContent]);

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
  }, [act, cardActionFetcher, shouldAct]);

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
