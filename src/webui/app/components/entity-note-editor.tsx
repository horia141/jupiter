import type { Note } from "@jupiter/webapi-client";
import { Box, useTheme } from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { Buffer } from "buffer-polyfill";
import type { ComponentType } from "react";
import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { ClientOnly } from "remix-utils/client-only";
import type { SomeErrorNoData } from "~/logic/action-result";
import type { OneOfNoteContentBlock } from "~/logic/domain/notes";
import type { BlockEditorProps } from "./infra/block-editor";
import { FieldError, GlobalError } from "./infra/errors";

const BlockEditor = lazy(() =>
  import("~/components/infra/block-editor.js").then((module) => ({
    default: module.default as unknown as ComponentType<BlockEditorProps>,
  })),
);

interface EntityNoteEditorProps {
  autofocus?: boolean;
  initialNote: Note;
  inputsEnabled: boolean;
}

export function EntityNoteEditor({
  initialNote,
  inputsEnabled,
}: EntityNoteEditorProps) {
  const cardActionFetcher = useFetcher<SomeErrorNoData>();
  const theme = useTheme();

  const [dataModified, setDataModified] = useState(false);
  const [shouldAct, setShouldAct] = useState(false);
  const [isActing, setIsActing] = useState(false);
  const [hasActed, setHasActed] = useState(false);
  const [noteContent, setNoteContent] = useState<Array<OneOfNoteContentBlock>>(
    initialNote.content,
  );

  const act = useCallback(() => {
    setIsActing(true);
    const base64Content = Buffer.from(
      JSON.stringify(noteContent),
      "utf-8",
    ).toString("base64");
    // We already created this thing, we just need to update!
    cardActionFetcher.submit(
      {
        id: initialNote.ref_id,
        content: base64Content,
      },
      {
        method: "post",
        action: "/app/workspace/core/notes/update",
      },
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
      isActing &&
      cardActionFetcher.state === "idle" &&
      cardActionFetcher.data !== null
    ) {
      setIsActing(false);
      if (shouldAct) {
        act();
        setShouldAct(false);
      } else {
        setHasActed(true);
        setTimeout(() => {
          setHasActed(false);
        }, 1000);
      }
    }
  }, [act, isActing, cardActionFetcher, shouldAct]);

  return (
    <Box sx={{ position: "relative" }}>
      <GlobalError actionResult={cardActionFetcher.data} />
      <FieldError actionResult={cardActionFetcher.data} fieldName="/content" />
      {isActing && (
        <Box
          sx={{
            position: "absolute",
            top: "0rem",
            right: "0rem",
            color: theme.palette.text.disabled,
          }}
        >
          Saving...
        </Box>
      )}
      {hasActed && (
        <Box
          sx={{
            position: "absolute",
            top: "0rem",
            right: "0rem",
            color: theme.palette.text.disabled,
          }}
        >
          Saved!
        </Box>
      )}

      <ClientOnly fallback={<div>Loading... </div>}>
        {() => (
          <Suspense fallback={<div>Loading...</div>}>
            <Box id="entity-block-editor">
              <BlockEditor
                autofocus={false}
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
    </Box>
  );
}
