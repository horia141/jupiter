import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
  Switch,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import type { Project } from "jupiter-gen";
import { ApiError, Difficulty, Eisen, RecurringTaskPeriod } from "jupiter-gen";
import { z } from "zod";
import { CheckboxAsString, parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { periodName } from "~/logic/domain/period";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const CreateFormSchema = {
  name: z.string(),
  project: z.string(),
  period: z.nativeEnum(RecurringTaskPeriod),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.union([z.nativeEnum(Difficulty), z.literal("default")]),
  actionableFromDay: z.string().optional(),
  actionableFromMonth: z.string().optional(),
  dueAtTime: z.string().optional(),
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
    const result = await getLoggedInApiClient(session).chore.createChore({
      name: { the_name: form.name },
      project_ref_id: { the_id: form.project },
      period: form.period,
      eisen: form.eisen,
      difficulty: form.difficulty === "default" ? undefined : form.difficulty,
      actionable_from_day: form.actionableFromDay
        ? { the_day: parseInt(form.actionableFromDay) }
        : undefined,
      actionable_from_month: form.actionableFromMonth
        ? { the_month: parseInt(form.actionableFromMonth) }
        : undefined,
      due_at_time: form.dueAtTime ? { the_time: form.dueAtTime } : undefined,
      due_at_day: form.dueAtDay
        ? { the_day: parseInt(form.dueAtDay) }
        : undefined,
      due_at_month: form.dueAtMonth
        ? { the_month: parseInt(form.dueAtMonth) }
        : undefined,
      must_do: form.mustDo,
      start_at_date: form.startAtDate
        ? { the_date: form.startAtDate, the_datetime: undefined }
        : undefined,
      end_at_date: form.endAtDate
        ? { the_date: form.endAtDate, the_datetime: undefined }
        : undefined,
    });

    return redirect(`/workspace/chores/${result.new_chore.ref_id.the_id}`);
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

export default function NewChore() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafCard returnLocation="/workspace/chores">
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

            <FormControl fullWidth>
              <InputLabel id="project">Project</InputLabel>
              <Select
                labelId="project"
                name="project"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.defaultProject.ref_id.the_id}
                label="Project"
              >
                {loaderData.allProjects.map((p: Project) => (
                  <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                    {p.name.the_name}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/project" />
            </FormControl>

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
              <FieldError actionResult={actionData} fieldName="/difficulty" />
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
              <FieldError actionResult={actionData} fieldName="/eisen" />
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
              <InputLabel id="dueAtTime">Due At Time</InputLabel>
              <OutlinedInput
                label="Due At Time"
                name="dueAtTime"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/due_at_time" />
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
              <FormControlLabel
                control={<Switch name="mustDo" readOnly={!inputsEnabled} />}
                label="Must Do"
              />
              <FieldError actionResult={actionData} fieldName="/must_do" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="skipRule">Skip Rule</InputLabel>
              <OutlinedInput
                label="Skip Rule"
                name="skipRule"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/skip_rule" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="startAtDate">Start At date</InputLabel>
              <OutlinedInput
                type="date"
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
              <InputLabel id="endAtDate">End At Date</InputLabel>
              <OutlinedInput
                type="date"
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
  () => `There was an error creating the chore! Please try again!`
);
