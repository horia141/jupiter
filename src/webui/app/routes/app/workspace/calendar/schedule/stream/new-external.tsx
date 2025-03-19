import { ApiError, ScheduleStreamColor } from "@jupiter/webapi-client";
import {
  Divider,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
  Typography,
} from "@mui/material";
import type { ActionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";

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
import { TopLevelInfoContext } from "~/top-level-context";

const CreateFormSchema = {
  sourceIcalUrl: z.string(),
  color: z.nativeEnum(ScheduleStreamColor),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);
  const url = new URL(request.url);

  try {
    const response = await apiClient.stream.scheduleStreamCreateForExternalIcal(
      {
        source_ical_url: form.sourceIcalUrl,
        color: form.color,
      }
    );

    return redirect(
      `/app/workspace/calendar/schedule/stream/${response.new_schedule_stream.ref_id}?${url.searchParams}`
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
  const [query] = useSearchParams();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel
      key="schedule-stream/new"
      returnLocation={`/app/workspace/calendar/schedule/stream?${query}`}
      inputsEnabled={inputsEnabled}
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
          <Typography variant="body1">
            In Google Calendar be sure to use the secret address in iCal format.
          </Typography>
          <Divider />
          <FormControl fullWidth>
            <InputLabel id="sourceIcalUrl">Source iCal URL</InputLabel>
            <OutlinedInput
              label="sourceIcalUrl"
              name="sourceIcalUrl"
              readOnly={!inputsEnabled}
            />
            <FieldError
              actionResult={actionData}
              fieldName="/source_ical_url"
            />
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

export const ErrorBoundary = makeLeafErrorBoundary(
  () => `/app/workspace/calendar/schedule/stream?${useSearchParams()}`,
  () => `There was an error creating the schedule stream! Please try again!`
);
