import type { InboxTask } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  NoteDomain,
  PersonRelationship,
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
import {
  ActionFunctionArgs,
  json,
  LoaderFunctionArgs,
  redirect,
} from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useFetcher,
  useParams,
  useNavigation,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { RecurringTaskGenParamsBlock } from "~/components/recurring-task-gen-params-block";
import { StandardDivider } from "~/components/standard-divider";
import { TimeEventFullDaysBlockStack } from "~/components/time-event-full-days-block-stack";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import {
  birthdayFromParts,
  extractBirthday,
} from "~/logic/domain/person-birthday";
import { personRelationshipName } from "~/logic/domain/person-relationship";
import { sortBirthdayTimeEventsNaturally } from "~/logic/domain/time-event";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const QuerySchema = {
  catchUpTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
  birthdayTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    relationship: z.nativeEnum(PersonRelationship),
    birthdayDay: z.string().optional(),
    birthdayMonth: z.string().optional(),
    catchUpPeriod: z
      .union([z.nativeEnum(RecurringTaskPeriod), z.literal("none")])
      .optional(),
    catchUpEisen: z.nativeEnum(Eisen).optional(),
    catchUpDifficulty: z.nativeEnum(Difficulty).optional(),
    catchUpActionableFromDay: z.string().optional(),
    catchUpActionableFromMonth: z.string().optional(),
    catchUpDueAtDay: z.string().optional(),
    catchUpDueAtMonth: z.string().optional(),
  }),
  z.object({
    intent: z.literal("regen"),
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
  const query = parseQuery(request, QuerySchema);

  try {
    const result = await apiClient.persons.personLoad({
      ref_id: id,
      allow_archived: true,
      catch_up_task_retrieve_offset: query.catchUpTasksRetrieveOffset,
      birthday_task_retrieve_offset: query.birthdayTasksRetrieveOffset,
    });

    return json({
      person: result.person,
      catchUpTasks: result.catch_up_tasks,
      catchUpTasksTotalCnt: result.catch_up_tasks_total_cnt,
      catchUpTasksPageSize: result.catch_up_tasks_page_size,
      birthdayTasks: result.birthday_tasks,
      birthdayTasksTotalCnt: result.birthday_tasks_total_cnt,
      birthdayTasksPageSize: result.birthday_tasks_page_size,
      note: result.note,
      birthdayTimeEventBlocks: result.birthday_time_event_blocks,
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
        await apiClient.persons.personUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          relationship: {
            should_change: true,
            value: form.relationship as PersonRelationship,
          },
          catch_up_period: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : (form.catchUpPeriod as RecurringTaskPeriod),
          },
          catch_up_eisen: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : (form.catchUpEisen as Eisen),
          },
          catch_up_difficulty: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : (form.catchUpDifficulty as Difficulty),
          },
          catch_up_actionable_from_day: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : form.catchUpActionableFromDay === undefined ||
                    form.catchUpActionableFromDay === ""
                  ? undefined
                  : parseInt(form.catchUpActionableFromDay),
          },
          catch_up_actionable_from_month: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : form.catchUpActionableFromMonth === undefined ||
                    form.catchUpActionableFromMonth === ""
                  ? undefined
                  : parseInt(form.catchUpActionableFromMonth),
          },
          catch_up_due_at_day: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : form.catchUpDueAtDay === undefined ||
                    form.catchUpDueAtDay === ""
                  ? undefined
                  : parseInt(form.catchUpDueAtDay),
          },
          catch_up_due_at_month: {
            should_change: true,
            value:
              form.catchUpPeriod === undefined || form.catchUpPeriod === "none"
                ? undefined
                : form.catchUpDueAtMonth === undefined ||
                    form.catchUpDueAtMonth === ""
                  ? undefined
                  : parseInt(form.catchUpDueAtMonth),
          },
          birthday: {
            should_change: true,
            value:
              form.birthdayDay === undefined ||
              form.birthdayDay === "N/A" ||
              form.birthdayMonth === undefined ||
              form.birthdayMonth === "N/A"
                ? undefined
                : birthdayFromParts(
                    parseInt(form.birthdayDay, 10),
                    parseInt(form.birthdayMonth, 10),
                  ),
          },
        });

        return redirect(`/app/workspace/persons`);
      }

      case "regen": {
        await apiClient.persons.personRegen({
          ref_id: id,
        });

        return redirect(`/app/workspace/persons/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.PERSON,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/persons/${id}`);
      }

      case "archive": {
        await apiClient.persons.personArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/persons`);
      }

      case "remove": {
        await apiClient.persons.personRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/persons`);
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

export default function Person() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const params = useParams();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const person = loaderData.person;
  const personBirthday = person.birthday
    ? extractBirthday(person.birthday)
    : undefined;

  const sortedBirthdayTasks = sortInboxTasksNaturally(
    loaderData.birthdayTasks,
    {
      dueDateAscending: false,
    },
  );
  const sortedCatchUpTasks = sortInboxTasksNaturally(loaderData.catchUpTasks, {
    dueDateAscending: false,
  });

  const birthdayTimeEventEntries = loaderData.birthdayTimeEventBlocks
    .filter((f) => !f.archived)
    .map((block) => ({
      time_event: block,
      entry: {
        person: person,
        birthday_time_event: block,
      },
    }));
  const sortedBirthdayTimeEventEntries = sortBirthdayTimeEventsNaturally(
    birthdayTimeEventEntries,
  );

  const inputsEnabled = navigation.state === "idle" && !person.archived;

  const cardActionFetcher = useFetcher();

  function handleCardMarkDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.DONE,
      },
      {
        method: "post",
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  function handleCardMarkNotDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`person-${person.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={person.archived}
      returnLocation="/app/workspace/persons"
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={person.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="relationship">Relationship</InputLabel>
              <Select
                labelId="relationship"
                name="relationship"
                readOnly={!inputsEnabled}
                defaultValue={person.relationship}
                label="Relationship"
              >
                {Object.values(PersonRelationship).map((relationship) => (
                  <MenuItem key={relationship} value={relationship}>
                    {personRelationshipName(relationship)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/relationship" />
            </FormControl>

            <Stack spacing={2} useFlexGap direction="row">
              <FormControl fullWidth>
                <InputLabel id="birthdayDay">
                  Birthday Day [Optional]
                </InputLabel>
                <Select
                  labelId="birthdayDay"
                  name="birthdayDay"
                  readOnly={!inputsEnabled}
                  defaultValue={personBirthday?.day ?? "N/A"}
                  label="Birthday Day"
                >
                  <MenuItem value={"N/A"}>N/A</MenuItem>
                  <MenuItem value={1}>1st</MenuItem>
                  <MenuItem value={2}>2nd</MenuItem>
                  <MenuItem value={3}>3rd</MenuItem>
                  <MenuItem value={4}>4th</MenuItem>
                  <MenuItem value={5}>5th</MenuItem>
                  <MenuItem value={6}>6th</MenuItem>
                  <MenuItem value={7}>7th</MenuItem>
                  <MenuItem value={8}>8th</MenuItem>
                  <MenuItem value={9}>9th</MenuItem>
                  <MenuItem value={10}>10th</MenuItem>
                  <MenuItem value={11}>11th</MenuItem>
                  <MenuItem value={12}>12th</MenuItem>
                  <MenuItem value={13}>13th</MenuItem>
                  <MenuItem value={14}>14th</MenuItem>
                  <MenuItem value={15}>15th</MenuItem>
                  <MenuItem value={16}>16th</MenuItem>
                  <MenuItem value={17}>17th</MenuItem>
                  <MenuItem value={18}>18th</MenuItem>
                  <MenuItem value={19}>19th</MenuItem>
                  <MenuItem value={20}>20th</MenuItem>
                  <MenuItem value={21}>21st</MenuItem>
                  <MenuItem value={22}>22nd</MenuItem>
                  <MenuItem value={23}>23rd</MenuItem>
                  <MenuItem value={24}>24th</MenuItem>
                  <MenuItem value={25}>25th</MenuItem>
                  <MenuItem value={26}>26th</MenuItem>
                  <MenuItem value={27}>27th</MenuItem>
                  <MenuItem value={28}>28th</MenuItem>
                  <MenuItem value={29}>29th</MenuItem>
                  <MenuItem value={30}>30th</MenuItem>
                  <MenuItem value={31}>31st</MenuItem>
                </Select>

                <FieldError actionResult={actionData} fieldName="/birthday" />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="birthdayMonth">
                  Birthday Month [Optional]
                </InputLabel>
                <Select
                  labelId="birthdayMonth"
                  name="birthdayMonth"
                  readOnly={!inputsEnabled}
                  defaultValue={personBirthday?.month ?? "N/A"}
                  label="Birthday Month"
                >
                  <MenuItem value={"N/A"}>N/A</MenuItem>
                  <MenuItem value={1}>January</MenuItem>
                  <MenuItem value={2}>February</MenuItem>
                  <MenuItem value={3}>March</MenuItem>
                  <MenuItem value={4}>April</MenuItem>
                  <MenuItem value={5}>May</MenuItem>
                  <MenuItem value={6}>June</MenuItem>
                  <MenuItem value={7}>July</MenuItem>
                  <MenuItem value={8}>August</MenuItem>
                  <MenuItem value={9}>September</MenuItem>
                  <MenuItem value={10}>October</MenuItem>
                  <MenuItem value={11}>November</MenuItem>
                  <MenuItem value={12}>December</MenuItem>
                </Select>
                <FieldError actionResult={actionData} fieldName="/birthday" />
              </FormControl>
            </Stack>

            <StandardDivider title="Catch Up" size="small" />

            <RecurringTaskGenParamsBlock
              namePrefix="catchUp"
              fieldsPrefix="catch_up"
              allowNonePeriod
              period={person.catch_up_params?.period ?? "none"}
              eisen={person.catch_up_params?.eisen}
              difficulty={person.catch_up_params?.difficulty}
              actionableFromDay={person.catch_up_params?.actionable_from_day}
              actionableFromMonth={
                person.catch_up_params?.actionable_from_month
              }
              dueAtDay={person.catch_up_params?.due_at_day}
              dueAtMonth={person.catch_up_params?.due_at_month}
              inputsEnabled={inputsEnabled}
              actionData={actionData}
            />
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
            <Button
              variant="outlined"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="regen"
            >
              Regen
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

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

      {sortedBirthdayTasks.length > 0 && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Birthday Tasks"
          inboxTasks={sortedBirthdayTasks}
          withPages={{
            retrieveOffsetParamName: "birthdayTasksRetrieveOffset",
            totalCnt: loaderData.birthdayTasksTotalCnt,
            pageSize: loaderData.birthdayTasksPageSize,
          }}
        />
      )}

      {sortedCatchUpTasks.length > 0 && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Catch Up Tasks"
          inboxTasks={sortedCatchUpTasks}
          withPages={{
            retrieveOffsetParamName: "catchUpTasksRetrieveOffset",
            totalCnt: loaderData.catchUpTasksTotalCnt,
            pageSize: loaderData.catchUpTasksPageSize,
          }}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.SCHEDULE,
      ) &&
        sortedBirthdayTimeEventEntries.length > 0 && (
          <TimeEventFullDaysBlockStack
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            title="Birthday Time Events"
            entries={sortedBirthdayTimeEventEntries}
          />
        )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary("/app/workspace/persons", {
  notFound: () => `Could not find person #${useParams().id}!`,
  error: () =>
    `There was an error loading person #${useParams().id}! Please try again!`,
});
