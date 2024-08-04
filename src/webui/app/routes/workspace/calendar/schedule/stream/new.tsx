import { ApiError, ScheduleStreamColor } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { ActionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
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
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const CreateFormSchema = {
  name: z.string(),
  color: z.nativeEnum(ScheduleStreamColor),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, CreateFormSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).stream.scheduleStreamCreateForUser({
      name: form.name,
      color: form.color,
    });

    return redirect(
      `/workspace/calendar/schedule/stream/${response.new_schedule_stream.ref_id}`
    );
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

export default function ScheduleStreamNew() {
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel
      key="schedule-stream/new"
      returnLocation="/workspace/calendar/schedule/stream"
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
                text: "Create",
                value: "create",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput label="name" name="name" readOnly={!inputsEnabled} />
            <FieldError actionResult={actionData} fieldName="/name" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="color">Color</InputLabel>
            <ScheduleStreamColorInput
              labelId="color"
              label="Color"
              name="color"
              value={ScheduleStreamColor.BLUE}
              readOnly={!inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/color" />
          </FormControl>
        </Stack>
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the project! Please try again!`
);
