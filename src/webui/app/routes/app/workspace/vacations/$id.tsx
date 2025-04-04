import { ApiError, NoteDomain, WorkspaceFeature } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TimeEventFullDaysBlockStack } from "~/components/time-event-full-days-block-stack";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};
const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    startDate: z.string(),
    endDate: z.string(),
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  try {
    const result = await apiClient.vacations.vacationLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      vacation: result.vacation,
      note: result.note,
      timeEventBlock: result.time_event_block,
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.vacations.vacationUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          start_date: {
            should_change: true,
            value: form.startDate,
          },
          end_date: {
            should_change: true,
            value: form.endDate,
          },
        });

        return redirect(`/app/workspace/vacations`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.VACATION,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/vacations/${id}`);
      }

      case "archive": {
        await apiClient.vacations.vacationArchive({
          ref_id: id,
        });
        return redirect(`/app/workspace/vacations`);
      }

      case "remove": {
        await apiClient.vacations.vacationRemove({
          ref_id: id,
        });
        return redirect(`/app/workspace/vacations`);
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Vacation() {
  const { vacation, note, timeEventBlock } =
    useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle" && !vacation.archived;

  const timeEventBlockEntry = {
    time_event: timeEventBlock,
    entry: {
      vacation: vacation,
      time_event: timeEventBlock,
    },
  };

  return (
    <LeafPanel
      key={`vacation-${vacation.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={vacation.archived}
      returnLocation="/app/workspace/vacations"
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={vacation.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="startDate" shrink>
                Start Date
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="startDate"
                defaultValue={aDateToDate(vacation.start_date).toFormat(
                  "yyyy-MM-dd",
                )}
                name="startDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/start_date" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="endDate" shrink>
                End Date
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="endDate"
                defaultValue={aDateToDate(vacation.end_date).toFormat(
                  "yyyy-MM-dd",
                )}
                name="endDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/end_date" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="vacation-update"
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

      <Card>
        {!note && (
          <CardActions>
            <ButtonGroup>
              <Button
                id="vacation-create-note"
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {note && (
          <>
            <EntityNoteEditor
              initialNote={note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.SCHEDULE,
      ) && (
        <TimeEventFullDaysBlockStack
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          title="Time Events"
          entries={[timeEventBlockEntry]}
        />
      )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary("/app/workspace/vacations", {
  notFound: () => `Could not find vacation #${useParams().id}!`,
  error: () =>
    `There was an error loading vacation #${useParams().id}! Please try again!`,
});
