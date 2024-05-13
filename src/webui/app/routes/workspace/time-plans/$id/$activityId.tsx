import { ApiError, NoteDomain } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  Switch,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TagsEditor } from "~/components/tags-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
  activityId: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  kind: z.nativeEnum(TimePlanActivityKind),
  feasability: z.nativeEnum(TImePlanActivityFeasability),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id, activityId } = parseParams(params, ParamsSchema);

  try {
    const result = await getLoggedInApiClient(
      session
    ).timePlans.timePlanActivityLoad({
        ref_id: activityId
    });

    return json({
      timePlanActivity: result.time_plan_activity,
      targetInboxTask: result.target_inbox_task,
      targetBigPlan: result.target_big_plan
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.NOT_FOUND) {
      throw new Response(ReasonPhrases.NOT_FOUND, {
        status: StatusCodes.NOT_FOUND,
        statusText: ReasonPhrases.NOT_FOUND,
      });
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id, activityId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(session).timePlans.timePlanActivityUpdate({
          ref_id: activityId,
          kind: {
            should_change: true,
            value: form.kind,
          },
          feasability: {
            should_change: true,
            value: form.feasability
          }
        });

        return redirect(`/workspace/time-plans/${id}/${activityId}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).timePlans.timePlanActivityArchive({
          ref_id: activityId,
        });

        return redirect(`/workspace/time-plans/${id}/${activityId}`);
      }
      default:
        throw new Response("Bad Intent", { status: 500 });
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

export default function TimePlanActivity() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.item.archived;

  return (
    <LeafPanel
      key={loaderData.item.ref_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/time-plans/${id}`}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>

            <FormControl fullWidth>
                <InputLabel id="kind">Kind</InputLabel>
                <ButtonGroup>
                    <Button
                        variant="contained"
                        disabled={!inputsEnabled}
                        name="kind"
                        value={TimePlanActivityKind.FINISH}>Finish</Button>
                    <Button
                        variant="contained"
                        disabled={!inputsEnabled}
                        name="kind"
                        value={TimePlanActivityKind.MAKE_PROGRESS}>Make Progress</Button>
                </ButtonGroup>
              <FieldError actionResult={actionData} fieldName="/kind" />
            </FormControl>

            <FormControl fullWidth>
                <InputLabel id="feasability">Feasability</InputLabel>
                <ButtonGroup>
                    <Button
                        variant="contained"
                        disabled={!inputsEnabled}
                        name="feasability"
                        value={TimePlanActivityFeasability.MUST_DO}>Must Do</Button>
                    <Button
                        variant="contained"
                        disabled={!inputsEnabled}
                        name="feasability"
                        value={TimePlanActivityFeasability.NICE_TO_HAVE}>Nice To Have</Button>
                    <Button
                        variant="contained"
                        disabled={!inputsEnabled}
                        name="feasability"
                        value={TimePlanActivityFeasability.STRETCH}>Stretch</Button>
                </ButtonGroup>
              <FieldError actionResult={actionData} fieldName="/feasability" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () =>
    `Could not find time plan activity #${useParams().id}:#${useParams().itemId}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${useParams().id}:#${
      useParams().activityId
    }! Please try again!`
);
