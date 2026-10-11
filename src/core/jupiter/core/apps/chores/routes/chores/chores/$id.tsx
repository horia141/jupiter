import type {
  AspectSummary,
  ChapterSummary,
  Contact,
  GoalSummary,
  InboxTask,
  LifePlan,
  MilestoneSummary,
  ChoreStack,
  Tag,
} from "@jupiter/webapi-client";
import {
  NamedEntityTag,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import type {
  ActionFunctionArgs,
  LoaderFunctionArgs,
  ShouldRevalidateFunction,
} from "react-router";
import {
  redirect,
  useActionData,
  useFetcher,
  useNavigation,
} from "react-router";
import { useContext } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams, parseQuery } from "zodix";

import { isWorkspaceFeatureAvailable } from "#/core/workspaces/root";
import {
  sortInboxTaskTimeEventsNaturally,
  timeEventInDayBlockToTimezone,
} from "#/core/common/sub/time_events/time-event";
import { TimeEventInDayBlockStack } from "#/core/common/sub/time_events/sub/in_day_block/component/stack";
import {
  sortInboxTasksNaturally,
  type InboxTaskParent,
} from "#/core/common/sub/inbox_tasks/root";
import { EntityNoteEditor } from "#/core/infra/component/entity-note-editor";
import { ChorePropertiesEditor } from "#/core/apps/chores/component/properties-editor";
import { InboxTaskStack } from "#/core/common/sub/inbox_tasks/component/stack";
import { makeLeafErrorBoundary } from "#/core/infra/component/error-boundary";
import { GlobalError } from "#/core/infra/component/errors";
import { LeafPanel } from "#/core/infra/component/layout/leaf-panel";
import { DisplayType } from "#/core/infra/component/use-nested-entities";
import { TopLevelInfoContext } from "#/core/infra/top-level-context";
import { SectionCard } from "#/core/infra/component/section-card";
import {
  ActionSingle,
  NavSingle,
  SectionActions,
} from "#/core/infra/component/section-actions";
import { noteStdOwner } from "#/core/common/sub/notes/note-std-owner";
import {
  handleActionApiError,
  handleLoaderApiError,
} from "#/core/infra/errors.server";
import { accessStatusAllowsWriterOrAbove } from "#/core/common/sub/access/access-level";
import { TimePlanActivityList } from "#/core/apps/time_plans/sub/activity/component/list";
import {
  SchedulingParamsFormFields,
  schedulingParamsUpdateArgs,
} from "#/core/common/scheduling-params-form";
import { useLoaderDataSafeForAnimation } from "#/core/infra/component/use-loader-data-for-animation";
import { basicShouldRevalidate } from "#/core/infra/should-revalidate";
import { getLoggedInApiClient } from "#/core/infra/api-clients.server";

const ParamsSchema = z.object({
  id: z.string(),
});

const QuerySchema = z.object({
  inboxTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    aspect: z.string().optional(),
    chapter: z.string().optional(),
    goal: z.string().optional(),
    isKey: CheckboxAsString,
    eisen: z.nativeEnum(Eisen),
    difficulty: z.nativeEnum(Difficulty),
    actionableFromDay: z.string().optional(),
    actionableFromMonth: z.string().optional(),
    dueAtDay: z.string().optional(),
    dueAtMonth: z.string().optional(),
    mustDo: CheckboxAsString,
    suspended: CheckboxAsString,
    skipRule: z.string().optional(),
    startAtDate: z.string().optional(),
    endAtDate: z.string().optional(),
    stack: z.string().optional(),
    ...SchedulingParamsFormFields,
  }),
  z.object({
    intent: z.literal("gen"),
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
  z.object({
    intent: z.literal("create-publish"),
    publishOwner: z.string(),
  }),
  z.object({
    intent: z.literal("activate-publish"),
    publishEntityRefId: z.string(),
  }),
  z.object({
    intent: z.literal("to-draft-publish"),
    publishEntityRefId: z.string(),
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
    const summaryPromise = apiClient.application.getSummaries({
      include_workspace: true,
      include_life_plan: true,
      include_aspects: true,
      include_chapters: true,
      include_goals: true,
      include_milestones: true,
    });
    // Only this call depends on another one (the workspace's features), so it
    // chains off the summaries while everything else runs concurrently.
    const timePlanActivitiesPromise = summaryPromise.then(
      async (summaryResponse) => {
        if (
          !isWorkspaceFeatureAvailable(
            summaryResponse.workspace!,
            WorkspaceFeature.TIME_PLANS,
          )
        ) {
          return undefined;
        }
        const timePlanActivitiesResult =
          await apiClient.timePlans.timePlanActivityFindForTarget({
            allow_archived: true,
            target: `Chore:std:${id}`,
          });
        return timePlanActivitiesResult.entries;
      },
    );

    const [
      summaryResponse,
      allTags,
      allContacts,
      stacksResponse,
      result,
      timePlanActivities,
    ] = await Promise.all([
      summaryPromise,
      apiClient.tags.tagFind({
        allow_archived: false,
      }),
      apiClient.contacts.contactFind({
        allow_archived: false,
      }),
      apiClient.chores.choreStackFind({
        allow_archived: false,
        include_tags: false,
        include_notes: false,
        include_life_plan: false,
        include_chores: false,
      }),
      apiClient.chores.choreLoad({
        ref_id: id,
        allow_archived: true,
        inbox_task_retrieve_offset: query.inboxTasksRetrieveOffset,
      }),
      timePlanActivitiesPromise,
    ]);

    return {
      chore: result.chore,
      tags: result.tags,
      note: result.note,
      aspect: result.aspect,
      chapter: result.chapter,
      goal: result.goal,
      inboxTasks: result.inbox_tasks,
      inboxTasksTotalCnt: result.inbox_tasks_total_cnt,
      inboxTasksPageSize: result.inbox_tasks_page_size,
      lifePlan: summaryResponse.life_plan as LifePlan | null,
      allAspects: summaryResponse.aspects as Array<AspectSummary> | null,
      allChapters: summaryResponse.chapters as Array<ChapterSummary> | null,
      allGoals: summaryResponse.goals as Array<GoalSummary> | null,
      allMilestones:
        summaryResponse.milestones as Array<MilestoneSummary> | null,
      allTags: allTags.tags as Array<Tag>,
      contacts:
        (
          result as {
            contacts?: Array<Contact>;
          }
        ).contacts ?? [],
      location: result.location ?? null,
      allContacts: allContacts.contacts as Array<Contact>,
      allStacks: mergeCurrentStack(
        stacksResponse.entries.map((entry) => entry.chore_stack),
        result.stack ?? null,
      ),
      timeEventBlocks: result.time_event_blocks,
      publishEntity: result.publish_entity ?? null,
      owner: result.owner,
      accessStatus: result.access_status ?? null,
      timePlanActivities,
    };
  } catch (error) {
    handleLoaderApiError(error);
  }
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.chores.choreUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          is_key: {
            should_change: true,
            value: form.isKey,
          },
          aspect_ref_id:
            form.aspect !== undefined
              ? { should_change: true, value: form.aspect }
              : { should_change: false },
          chapter_ref_id:
            form.aspect !== undefined
              ? {
                  should_change: true,
                  value:
                    form.chapter !== undefined && form.chapter !== ""
                      ? form.chapter
                      : undefined,
                }
              : { should_change: false },
          goal_ref_id:
            form.aspect !== undefined
              ? {
                  should_change: true,
                  value:
                    form.goal !== undefined && form.goal !== ""
                      ? form.goal
                      : undefined,
                }
              : { should_change: false },
          stack_ref_id: {
            should_change: true,
            value:
              form.stack !== undefined && form.stack !== "" ? form.stack : null,
          },
          eisen: {
            should_change: true,
            value: form.eisen,
          },
          difficulty: {
            should_change: true,
            value: form.difficulty,
          },
          actionable_from_day: {
            should_change: true,
            value:
              form.actionableFromDay === undefined ||
              form.actionableFromDay === ""
                ? undefined
                : parseInt(form.actionableFromDay),
          },
          actionable_from_month: {
            should_change: true,
            value:
              form.actionableFromMonth === undefined ||
              form.actionableFromMonth === ""
                ? undefined
                : parseInt(form.actionableFromMonth),
          },
          due_at_day: {
            should_change: true,
            value:
              form.dueAtDay === undefined || form.dueAtDay === ""
                ? undefined
                : parseInt(form.dueAtDay),
          },
          due_at_month: {
            should_change: true,
            value:
              form.dueAtMonth === undefined || form.dueAtMonth === ""
                ? undefined
                : parseInt(form.dueAtMonth),
          },
          must_do: {
            should_change: true,
            value: form.mustDo,
          },
          suspended: {
            should_change: true,
            value: form.suspended,
          },
          skip_rule: {
            should_change: true,
            value:
              form.skipRule === undefined || form.skipRule === ""
                ? undefined
                : form.skipRule,
          },
          start_at_date: {
            should_change: true,
            value:
              form.startAtDate === undefined || form.startAtDate === ""
                ? undefined
                : form.startAtDate,
          },
          end_at_date: {
            should_change: true,
            value:
              form.endAtDate === undefined || form.endAtDate === ""
                ? undefined
                : form.endAtDate,
          },
          ...schedulingParamsUpdateArgs(form),
        });

        return redirect(`/app/workspace/apps/chores/chores`);
      }

      case "gen": {
        await apiClient.chores.choreRegen({
          ref_id: id,
        });

        return redirect(`/app/workspace/apps/chores/chores/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          owner: noteStdOwner(NamedEntityTag.CHORE, id),
          content: [],
        });

        return redirect(`/app/workspace/apps/chores/chores/${id}`);
      }

      case "archive": {
        await apiClient.chores.choreArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/apps/chores/chores`);
      }

      case "remove": {
        await apiClient.chores.choreRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/apps/chores/chores`);
      }

      case "create-publish": {
        await apiClient.publish.publishEntityCreate({
          owner: form.publishOwner,
        });

        return redirect(`/app/workspace/apps/chores/chores/${id}`);
      }

      case "activate-publish": {
        await apiClient.publish.publishEntityActivate({
          ref_id: form.publishEntityRefId,
        });

        return redirect(`/app/workspace/apps/chores/chores/${id}`);
      }

      case "to-draft-publish": {
        await apiClient.publish.publishEntityToDraft({
          ref_id: form.publishEntityRefId,
        });

        return redirect(`/app/workspace/apps/chores/chores/${id}`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
  } catch (error) {
    return handleActionApiError(error);
  }
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function Chore() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" &&
    !loaderData.chore.archived &&
    accessStatusAllowsWriterOrAbove(loaderData.accessStatus);

  const sortedInboxTasks = sortInboxTasksNaturally(loaderData.inboxTasks, {
    dueDateAscending: false,
  });
  const moreInfoByRefId: { [key: string]: InboxTaskParent } = {};
  for (const it of loaderData.inboxTasks) {
    moreInfoByRefId[it.ref_id] = {
      chore: loaderData.chore,
      choreStack: loaderData.allStacks.find(
        (stack) => stack.ref_id === loaderData.chore.stack_ref_id,
      ),
      owner: loaderData.owner,
      accessStatus: loaderData.accessStatus ?? undefined,
      location: loaderData.location ?? undefined,
    };
  }

  const timeEventEntries = loaderData.timeEventBlocks.map((block) => ({
    time_event_in_tz: timeEventInDayBlockToTimezone(
      block,
      topLevelInfo.user.timezone,
    ),
    entry: {
      chore: loaderData.chore,
      time_events: [block],
    },
  }));
  const sortedTimeEventEntries =
    sortInboxTaskTimeEventsNaturally(timeEventEntries);

  const cardActionFetcher = useFetcher();

  function handleCardMarkDone(it: InboxTask) {
    if (!inputsEnabled) {
      return;
    }
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.DONE,
      },
      {
        method: "post",
        action: "/app/workspace/core/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  function handleCardMarkNotDone(it: InboxTask) {
    if (!inputsEnabled) {
      return;
    }
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/app/workspace/core/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  return (
    <LeafPanel
      key={`chore-${loaderData.chore.ref_id}`}
      entityType={NamedEntityTag.CHORE}
      entityRefId={loaderData.chore.ref_id}
      fakeKey={`chore-{loaderData.chore.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.chore.archived}
      returnLocation="/app/workspace/apps/chores/chores"
      publishable
      publishEntity={loaderData.publishEntity ?? undefined}
      accessable
      accessOwner={loaderData.owner}
      accessStatus={loaderData.accessStatus}
    >
      <GlobalError actionResult={actionData} />
      <ChorePropertiesEditor
        title="Properties"
        topLevelInfo={topLevelInfo}
        lifePlan={loaderData.lifePlan}
        allAspects={loaderData.allAspects ?? []}
        allChapters={loaderData.allChapters ?? []}
        allGoals={loaderData.allGoals ?? []}
        allMilestones={loaderData.allMilestones ?? []}
        allTags={loaderData.allTags}
        tags={loaderData.tags}
        allContacts={loaderData.allContacts}
        contacts={loaderData.contacts}
        location={loaderData.location}
        inputsEnabled={inputsEnabled}
        entityOwner={loaderData.owner}
        chore={loaderData.chore}
        allStacks={loaderData.allStacks}
        aspect={loaderData.aspect}
        chapter={loaderData.chapter}
        goal={loaderData.goal}
        actionData={actionData}
      />

      <SectionCard
        title="Note"
        actions={
          <SectionActions
            id="chore-note"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Create Note",
                value: "create-note",
                highlight: false,
                disabled: loaderData.note !== null,
              }),
            ]}
          />
        }
      >
        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </SectionCard>

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.SCHEDULE,
      ) && (
        <TimeEventInDayBlockStack
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          title="Time Events"
          createLocation={`/app/workspace/calendar/time-event/in-day-block/new-for-chore?choreRefId=${loaderData.chore.ref_id}`}
          entries={sortedTimeEventEntries}
        />
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.TIME_PLANS,
      ) &&
        loaderData.timePlanActivities && (
          <SectionCard
            id="chore-time-plans"
            title="Time Plans"
            actions={
              <SectionActions
                id="chore-time-plans-actions"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  NavSingle({
                    text: "Add",
                    highlight: false,
                    link: `/app/workspace/apps/time-plans/add-chore-to-plans?choreRefId=${loaderData.chore.ref_id}`,
                  }),
                ]}
              />
            }
          >
            <TimePlanActivityList
              topLevelInfo={topLevelInfo}
              activities={loaderData.timePlanActivities.map(
                (entry) => entry.time_plan_activity,
              )}
              timePlansByRefId={
                new Map(
                  loaderData.timePlanActivities.map((entry) => [
                    entry.time_plan.ref_id,
                    entry.time_plan,
                  ]),
                )
              }
              inboxTasksByRefId={new Map()}
              bigPlansByRefId={new Map()}
              todoTasksByRefId={new Map()}
              habitsByRefId={new Map()}
              choresByRefId={
                new Map([[loaderData.chore.ref_id, loaderData.chore]])
              }
              activityDoneness={{}}
              timeEventsByRefId={new Map()}
              fullInfo={false}
              showTimePlanName={true}
            />
          </SectionCard>
        )}

      <SectionCard title="Inbox Tasks">
        {sortedInboxTasks.length > 0 && (
          <InboxTaskStack
            topLevelInfo={topLevelInfo}
            showOptions={{
              showStatus: true,
              showDueDate: true,
              showHandleMarkDone: inputsEnabled,
              showHandleMarkNotDone: inputsEnabled,
            }}
            inboxTasks={sortedInboxTasks}
            moreInfoByRefId={moreInfoByRefId}
            withPages={{
              retrieveOffsetParamName: "inboxTasksRetrieveOffset",
              totalCnt: loaderData.inboxTasksTotalCnt,
              pageSize: loaderData.inboxTasksPageSize,
            }}
            onCardMarkDone={inputsEnabled ? handleCardMarkDone : undefined}
            onCardMarkNotDone={
              inputsEnabled ? handleCardMarkNotDone : undefined
            }
          />
        )}
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/apps/chores/chores",
  ParamsSchema,
  {
    notFound: (params) => `Could not find chore #${params.id}!`,
    error: (params) =>
      `There was an error loading chore #${params.id}! Please try again!`,
  },
);

function mergeCurrentStack(
  stacks: ChoreStack[],
  current: ChoreStack | null,
): ChoreStack[] {
  if (current === null) {
    return stacks;
  }
  if (stacks.some((stack) => stack.ref_id === current.ref_id)) {
    return stacks;
  }
  return [...stacks, current];
}
