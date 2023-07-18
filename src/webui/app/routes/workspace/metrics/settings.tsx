import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import type { Project } from "jupiter-gen";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const UpdateFormSchema = {
  project: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_default_project: true,
    include_projects: true,
  });

  const metricSettingsResponse = await getLoggedInApiClient(
    session
  ).metric.loadMetricSettings({});

  return json({
    collectionProject: metricSettingsResponse.collection_project,
    defaultProject: summaryResponse.default_project as Project,
    allProjects: summaryResponse.projects as Array<Project>,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  try {
    await getLoggedInApiClient(session).metric.changeMetricCollectionProject({
      collection_project_ref_id: { the_id: form.project },
    });

    return redirect(`/workspace/metrics/settings`);
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

export default function MetricsSettings() {
  const transition = useTransition();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafCard returnLocation="/workspace/metrics">
      <Card>
        <GlobalError actionResult={actionData} />

        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="collectionProject">Collection Project</InputLabel>
              <Select
                labelId="collectionProject"
                name="collectionProject"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.collectionProject.ref_id.the_id}
                label="Collection Project"
              >
                {loaderData.allProjects.map((p) => (
                  <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                    {p.name.the_name}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/collection_project_ref_id"
              />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Change Collection Project
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error upserting the metric settings! Please try again!`
);
