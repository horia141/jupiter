import type { ProjectSummary } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  RecurringTaskPeriod,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
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
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/project-select";
import { RecurringTaskGenParamsBlock } from "~/components/recurring-task-gen-params-block";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const CreateFormSchema = {
  name: z.string(),
  project: z.string().optional(),
  period: z.nativeEnum(RecurringTaskPeriod),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.nativeEnum(Difficulty),
  actionableFromDay: z.string().optional(),
  actionableFromMonth: z.string().optional(),
  dueAtDay: z.string().optional(),
  dueAtMonth: z.string().optional(),
  mustDo: CheckboxAsString,
  skipRule: z.string().optional(),
  startAtDate: z.string().optional(),
  endAtDate: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  return json({
    rootProject: summaryResponse.root_project as ProjectSummary,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.chores.choreCreate({
      name: form.name,
      project_ref_id: form.project !== undefined ? form.project : undefined,
      period: form.period,
      eisen: form.eisen,
      difficulty: form.difficulty,
      actionable_from_day: form.actionableFromDay
        ? parseInt(form.actionableFromDay)
        : undefined,
      actionable_from_month: form.actionableFromMonth
        ? parseInt(form.actionableFromMonth)
        : undefined,
      due_at_day: form.dueAtDay ? parseInt(form.dueAtDay) : undefined,
      due_at_month: form.dueAtMonth ? parseInt(form.dueAtMonth) : undefined,
      skip_rule:
        form.skipRule !== undefined && form.skipRule !== ""
          ? form.skipRule
          : undefined,
      must_do: form.mustDo,
      start_at_date: form.startAtDate ? form.startAtDate : undefined,
      end_at_date: form.endAtDate ? form.endAtDate : undefined,
    });

    return redirect(`/workspace/chores/${result.new_chore.ref_id}`);
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

export default function NewChore() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel key={"chores/new"} returnLocation="/workspace/chores">
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={""}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <FormControl fullWidth>
                <ProjectSelect
                  name="project"
                  label="Project"
                  inputsEnabled={inputsEnabled}
                  disabled={false}
                  allProjects={loaderData.allProjects}
                  defaultValue={loaderData.rootProject.ref_id}
                />
                <FieldError actionResult={actionData} fieldName="/project" />
              </FormControl>
            )}

            <RecurringTaskGenParamsBlock
              inputsEnabled={inputsEnabled}
              allowSkipRule
              period={RecurringTaskPeriod.DAILY}
              eisen={Eisen.REGULAR}
              difficulty={Difficulty.EASY}
              actionableFromDay={null}
              actionableFromMonth={null}
              dueAtDay={null}
              dueAtMonth={null}
              skipRule={null}
              actionData={actionData}
            />

            <FormControl fullWidth>
              <FormControlLabel
                control={<Switch name="mustDo" readOnly={!inputsEnabled} />}
                label="Must Do In Vacation"
              />
              <FieldError actionResult={actionData} fieldName="/must_do" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="startAtDate" shrink>
                Start At date [Optional]
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="startAtDate"
                name="startAtDate"
                readOnly={!inputsEnabled}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/start_at_date"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="endAtDate" shrink>
                End At Date [Optional]
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="endAtDate"
                name="endAtDate"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/end_at_date" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="chore-create"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
            >
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the chore! Please try again!`
);
