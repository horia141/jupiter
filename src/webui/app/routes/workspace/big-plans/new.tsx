import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
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

const CreateFormSchema = {
  name: z.string(),
  project: z.string(),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
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

  return json({
    defaultProject: summaryResponse.default_project as Project,
    allProjects: summaryResponse.projects as Array<Project>,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await getLoggedInApiClient(session).bigPlan.createBigPlan({
      name: { the_name: form.name },
      project_ref_id: { the_id: form.project },
      actionable_date:
        form.actionableDate !== undefined && form.actionableDate !== ""
          ? { the_date: form.actionableDate, the_datetime: undefined }
          : undefined,
      due_date:
        form.dueDate !== undefined && form.dueDate !== ""
          ? { the_date: form.dueDate, the_datetime: undefined }
          : undefined,
    });

    return redirect(
      `/workspace/big-plans/${result.new_big_plan.ref_id.the_id}`
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

export default function NewBigPlan() {
  const transition = useTransition();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafCard returnLocation="/workspace/big-plans">
      <GlobalError actionResult={actionData} />
      <Card>
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="project">Project</InputLabel>
              <Select
                labelId="project"
                name="project"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.defaultProject.ref_id.the_id}
                label="Project"
              >
                {loaderData.allProjects.map((p) => (
                  <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                    {p.name.the_name}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/project" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="actionableDate" shrink margin="dense">
                Actionable From
              </InputLabel>
              <OutlinedInput
                type="date"
                label="actionableDate"
                name="actionableDate"
                readOnly={!inputsEnabled}
              />

              <FieldError
                actionResult={actionData}
                fieldName="/actionable_date"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="dueDate" shrink margin="dense">
                Due At
              </InputLabel>
              <OutlinedInput
                type="date"
                label="dueDate"
                name="dueDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/due_date" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the big plan! Please try again!`
);
