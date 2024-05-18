import { ApiError, EventSource, SyncTarget } from "@jupiter/webapi-client";
import ArchiveIcon from "@mui/icons-material/Archive";
import TuneIcon from "@mui/icons-material/Tune";
import { Button, Card, CardContent } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useTransition } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const UpdateFormSchema = {
  intent: z.string(),
};

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(
    session
  ).workingMem.workingMemLoadCurrent({});
  return json({
    entry: response.entry,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "generate-first-note": {
        await getLoggedInApiClient(session).gen.genDo({
          source: EventSource.WEB,
          gen_even_if_not_modified: false,
          gen_targets: [SyncTarget.WORKING_MEM],
        });

        return redirect("/workspace/working-mem");
      }

      default:
        throw new Error(`Unknown intent: ${intent}`);
    }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function WorkingMem() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const transition = useTransition();
  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const inputsEnabled = transition.state === "idle";

  return (
    <TrunkPanel
    key={"working-mem"}
      returnLocation="/workspace"
      extraControls={[
        <Button
          key="settings"
          component={Link}
          to="/workspace/working-mem/settings"
          variant="outlined"
          startIcon={<TuneIcon />}
        >
          Settings
        </Button>,
        <Button
          key="archive"
          component={Link}
          to="/workspace/working-mem/archive"
          variant="outlined"
          startIcon={<ArchiveIcon />}
        >
          Archive
        </Button>,
      ]}
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        <ToolPanel>
          <Card>
            <CardContent>
              {loaderData.entry && (
                <EntityNoteEditor
                  initialNote={loaderData.entry.note}
                  inputsEnabled={inputsEnabled}
                />
              )}

              {!loaderData.entry && (
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="generate-first-note"
                >
                  Generate First WorkingMem.txt Note
                </Button>
              )}
            </CardContent>
          </Card>
        </ToolPanel>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the working mem! Please try again!`
);
