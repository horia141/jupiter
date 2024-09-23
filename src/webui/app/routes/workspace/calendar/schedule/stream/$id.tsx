import {
  ApiError,
  EventSource,
  NoteDomain,
  ScheduleSource,
  ScheduleStreamColor,
} from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useParams,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ScheduleStreamColorInput } from "~/components/schedule-stream-color-input";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isCorePropertyEditable } from "~/logic/domain/schedule-stream";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    color: z.nativeEnum(ScheduleStreamColor),
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
  z.object({
    intent: z.literal("sync"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).stream.scheduleStreamLoad({ ref_id: id, allow_archived: true });

    return json({
      scheduleStream: response.schedule_stream,
      note: response.note,
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

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);
  const url = new URL(request.url);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(session).stream.scheduleStreamUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          color: {
            should_change: true,
            value: form.color,
          },
        });

        return redirect(
          `/workspace/calendar/schedule/stream/${id}?${url.searchParams}`
        );
      }

      case "create-note": {
        await getLoggedInApiClient(session).notes.noteCreate({
          domain: NoteDomain.SCHEDULE_STREAM,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(
          `/workspace/calendar/schedule/stream/${id}?${url.searchParams}`
        );
      }

      case "sync": {
        await getLoggedInApiClient(session).schedule.scheduleExternalSyncDo({
          source: EventSource.SCHEDULE_EXTERNAL_SYNC_CRON,
          filter_schedule_stream_ref_id: [id],
        });

        return redirect(
          `/workspace/calendar/schedule/stream/${id}?${url.searchParams}`
        );
      }

      case "archive": {
        await getLoggedInApiClient(session).stream.scheduleStreamArchive({
          ref_id: id,
        });

        return redirect(
          `/workspace/calendar/schedule/stream/${id}?${url.searchParams}`
        );
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

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function ScheduleStreamViewOne() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();
  const [query] = useSearchParams();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.scheduleStream.archived;
  const corePropertyEditable = isCorePropertyEditable(
    loaderData.scheduleStream
  );

  return (
    <LeafPanel
      key={`schedule-stream-${loaderData.scheduleStream.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/calendar/schedule/stream?${query}`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="schedule-stream-properties"
        title="Properties"
        actions={
          <SectionActions
            id="schedule-stream-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Save",
                value: "update",
                highlight: true,
              }),
              ActionSingle({
                text: "Sync",
                value: "sync",
                disabled: loaderData.scheduleStream.source !== ScheduleSource.EXTERNAL_ICAL,
              })
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          {loaderData.scheduleStream.source ===
            ScheduleSource.EXTERNAL_ICAL && (
            <FormControl fullWidth>
              <InputLabel id="sourceIcalUrl">Source iCal URL</InputLabel>
              <OutlinedInput
                label="sourceIcalUrl"
                name="sourceIcalUrl"
                defaultValue={loaderData.scheduleStream.source_ical_url!}
                readOnly={true}
              />
            </FormControl>
          )}

          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput
              label="name"
              name="name"
              readOnly={!inputsEnabled || !corePropertyEditable}
              defaultValue={loaderData.scheduleStream.name}
            />
            <FieldError actionResult={actionData} fieldName="/name" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="color">Color</InputLabel>
            <ScheduleStreamColorInput
              labelId="color"
              label="Color"
              name="color"
              value={loaderData.scheduleStream.color}
              readOnly={!inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/color" />
          </FormControl>
        </Stack>
      </SectionCardNew>

      <Card>
        {!loaderData.note && (
          <CardActions>
            <ButtonGroup>
              <Button
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

        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find schedule stream #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading schedule stream #${
      useParams().id
    }. Please try again!`
);
