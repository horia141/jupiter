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
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
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
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { periodName } from "~/logic/domain/period";
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
  difficulty: z.union([z.nativeEnum(Difficulty), z.literal("default")]),
  actionableFromDay: z.string().optional(),
  actionableFromMonth: z.string().optional(),
  dueAtDay: z.string().optional(),
  dueAtMonth: z.string().optional(),
  mustDo: CheckboxAsString,
  skipRule: z.string().optional(),
  repeatsInPeriodCount: z.string().optional(),
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
    const result = await apiClient.habits.habitCreate({
      name: form.name,
      project_ref_id: form.project !== undefined ? form.project : undefined,
      period: form.period,
      eisen: form.eisen,
      difficulty: form.difficulty === "default" ? undefined : form.difficulty,
      actionable_from_day: form.actionableFromDay
        ? parseInt(form.actionableFromDay)
        : undefined,
      actionable_from_month: form.actionableFromMonth
        ? parseInt(form.actionableFromMonth)
        : undefined,
      due_at_day: form.dueAtDay ? parseInt(form.dueAtDay) : undefined,
      due_at_month: form.dueAtMonth ? parseInt(form.dueAtMonth) : undefined,
      skip_rule: form.skipRule,
      repeats_in_period_count: form.repeatsInPeriodCount
        ? parseInt(form.repeatsInPeriodCount)
        : undefined,
    });

    return redirect(`/workspace/habits/${result.new_habit.ref_id}`);
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

export default function NewHabit() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel key={"habits/new"} returnLocation="/workspace/habits">
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

            <FormControl fullWidth>
              <InputLabel id="period">Period</InputLabel>
              <Select
                labelId="status"
                name="period"
                readOnly={!inputsEnabled}
                defaultValue={RecurringTaskPeriod.DAILY}
                label="Period"
              >
                {Object.values(RecurringTaskPeriod).map((s) => (
                  <MenuItem key={s} value={s}>
                    {periodName(s)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/status" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <FormControl fullWidth>
                <InputLabel id="project">Project</InputLabel>
                <Select
                  labelId="project"
                  name="project"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.rootProject.ref_id}
                  label="Project"
                >
                  {loaderData.allProjects.map((p) => (
                    <MenuItem key={p.ref_id} value={p.ref_id}>
                      {p.name}
                    </MenuItem>
                  ))}
                </Select>
                <FieldError actionResult={actionData} fieldName="/project" />
              </FormControl>
            )}

            <FormControl fullWidth>
              <InputLabel id="eisen">Eisenhower</InputLabel>
              <Select
                labelId="eisen"
                name="eisen"
                readOnly={!inputsEnabled}
                defaultValue={Eisen.REGULAR}
                label="Eisen"
              >
                {Object.values(Eisen).map((e) => (
                  <MenuItem key={e} value={e}>
                    {eisenName(e)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/eisen" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="difficulty">Difficulty</InputLabel>
              <Select
                labelId="difficulty"
                name="difficulty"
                readOnly={!inputsEnabled}
                defaultValue={"default"}
                label="Difficulty"
              >
                <MenuItem value="default">Default</MenuItem>
                {Object.values(Difficulty).map((e) => (
                  <MenuItem key={e} value={e}>
                    {difficultyName(e)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/difficulty" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="actionableFromDay">
                Actionable From Day
              </InputLabel>
              <OutlinedInput
                label="Actionable From Day"
                name="actionableFromDay"
                readOnly={!inputsEnabled}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/actionable_from_day"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="actionableFromMonth">
                Actionable From Month
              </InputLabel>
              <OutlinedInput
                label="Actionable From Month"
                name="actionableFromMonth"
                readOnly={!inputsEnabled}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/actionable_from_month"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="dueAtDay">Due At Day</InputLabel>
              <OutlinedInput
                label="Due At Day"
                name="dueAtDay"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/due_at_day" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="dueAtMonth">Due At Month</InputLabel>
              <OutlinedInput
                label="Due At Month"
                name="dueAtMonth"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/due_at_month" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="repeatsInPeriodCount">
                Repeats In Period
              </InputLabel>
              <OutlinedInput
                label="Repeats In Period"
                name="repeatsInPeriodCount"
                readOnly={!inputsEnabled}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/repeats_in_period_count"
              />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="habit-create"
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
  () => `There was an error creating the habit! Please try again!`
);
