import type {
  Aspect,
  AspectSummary,
  Chapter,
  ChapterSummary,
  Contact,
  Goal,
  GoalSummary,
  Habit,
  HabitRepeatsStrategy,
  HabitStack,
  LifePlan,
  Location,
  MilestoneSummary,
  Tag,
  UserLight,
} from "@jupiter/webapi-client";
import {
  NamedEntityTag,
  RecurringTaskPeriod,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import {
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  Switch,
} from "@mui/material";
import { useMemo, useState } from "react";
import { Launch as LaunchIcon } from "@mui/icons-material";

import { aDateToDate } from "#/core/common/adate";
import { entityLinkStd } from "#/core/common/entity-link";
import { IsKeySelect } from "#/core/common/component/is-key-select";
import { RecurringTaskGenParamsBlock } from "#/core/common/component/recurring-task-gen-params-block";
import { SchedulingParamsBlock } from "#/core/common/component/scheduling-params-block";
import { ContactsEditor } from "#/core/common/sub/contacts/component/contacts-editor";
import { EntityLocationMapSection } from "#/core/common/sub/locations/component/entity-location-map-section";
import { LocationsEditor } from "#/core/common/sub/locations/component/locations-editor";
import { TagsEditor } from "#/core/common/sub/tags/component/tags-editor";
import { HabitRepeatStrategySelect } from "#/core/apps/habits/component/repeat-strategy-select";
import { HabitStackSelectSingle } from "#/core/apps/habits/component/stack-select-single";
import type { SomeErrorNoData } from "#/core/infra/action-result";
import { FieldError } from "#/core/infra/component/errors";
import {
  ActionSingle,
  NavSingle,
  SectionActions,
} from "#/core/infra/component/section-actions";
import { SectionCard } from "#/core/infra/component/section-card";
import { useBigScreen } from "#/core/infra/component/use-big-screen";
import { constructFieldName } from "#/core/infra/field-names";
import type { TopLevelInfo } from "#/core/infra/top-level-context";
import { LifePlanAssociations } from "#/core/apps/life_plan/components/life-plan-associations";
import { lifePlanBirthdayDate } from "#/core/apps/life_plan/root";
import { isWorkspaceFeatureAvailable } from "#/core/workspaces/root";

interface HabitPropertiesEditorProps {
  title: string;
  showLinkToHabit?: boolean;
  showGen?: boolean;
  intentPrefix?: string;
  namePrefix?: string;
  topLevelInfo: TopLevelInfo;
  lifePlan: LifePlan | null;
  allAspects: AspectSummary[];
  allChapters: ChapterSummary[];
  allGoals: GoalSummary[];
  allMilestones: MilestoneSummary[];
  aspect?: Aspect | null;
  chapter?: Chapter | null;
  goal?: Goal | null;
  allTags: Array<Tag>;
  tags: Array<Tag>;
  allContacts: Array<Contact>;
  contacts: Array<Contact>;
  location?: Location | null;
  inputsEnabled: boolean;
  entityOwner?: UserLight;
  habit: Habit;
  allStacks?: HabitStack[];
  actionData?: SomeErrorNoData;
}

export function HabitPropertiesEditor(props: HabitPropertiesEditorProps) {
  const isBigScreen = useBigScreen();
  const birthdayDate = props.lifePlan
    ? lifePlanBirthdayDate(props.lifePlan)
    : null;
  const [selectedAspectRefId, setSelectedAspectRefId] = useState(
    props.habit.aspect_ref_id,
  );
  const [selectedPeriod, setSelectedPeriod] = useState(
    props.habit.gen_params.period,
  );
  const [selectedStackRefId, setSelectedStackRefId] = useState<
    string | undefined
  >(props.habit.stack_ref_id ?? undefined);
  const [selectedRepeatsStrategy, setSelectedRepeatsStrategy] = useState<
    HabitRepeatsStrategy | "none"
  >(props.habit.repeats_strategy ?? "none");
  const showGen = props.showGen ?? true;

  // Shared habits may reference life-plan entities from another workspace.
  // Include those for display, but keep associations read-only.
  const lifePlanAssociationsInWorkspace = props.allAspects.some(
    (aspect) => aspect.ref_id === props.habit.aspect_ref_id,
  );
  const allAspects = useMemo(
    () =>
      mergeForeignAspectSummary(
        props.allAspects,
        props.aspect,
        props.habit.aspect_ref_id,
      ),
    [props.allAspects, props.aspect, props.habit.aspect_ref_id],
  );
  const allChapters = useMemo(
    () =>
      mergeForeignChapterSummary(
        props.allChapters,
        props.chapter,
        props.habit.chapter_ref_id,
      ),
    [props.allChapters, props.chapter, props.habit.chapter_ref_id],
  );
  const allGoals = useMemo(
    () =>
      mergeForeignGoalSummary(
        props.allGoals,
        props.goal,
        props.habit.goal_ref_id,
      ),
    [props.allGoals, props.goal, props.habit.goal_ref_id],
  );

  return (
    <>
      <SectionCard
        title={props.title}
        actions={
          <SectionActions
            id="habit-properties"
            topLevelInfo={props.topLevelInfo}
            inputsEnabled={props.inputsEnabled}
            actions={[
              ActionSingle({
                id: "habit-update",
                text: "Save",
                value: constructIntentName(props.intentPrefix, "update"),
                highlight: true,
              }),
              ...(showGen
                ? [
                    ActionSingle({
                      text: "Gen",
                      value: constructIntentName(props.intentPrefix, "gen"),
                      highlight: false,
                    }),
                  ]
                : []),
            ]}
            extraActions={
              props.showLinkToHabit
                ? [
                    NavSingle({
                      text: "Habit",
                      link: `/app/workspace/apps/habits/habits/${props.habit.ref_id}`,
                      icon: <LaunchIcon />,
                    }),
                  ]
                : undefined
            }
          />
        }
      >
        <input
          type="hidden"
          name={constructFieldName(props.namePrefix, "refId")}
          value={props.habit.ref_id}
        />

        <Stack
          direction="row"
          useFlexGap
          spacing={1}
          sx={{ flexWrap: "nowrap" }}
        >
          <FormControl sx={{ flex: "1 1 0", minWidth: 0 }}>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput
              label="Name"
              name={constructFieldName(props.namePrefix, "name")}
              readOnly={!props.inputsEnabled}
              disabled={!props.inputsEnabled}
              defaultValue={props.habit.name}
            />
            <FieldError actionResult={props.actionData} fieldName="/name" />
          </FormControl>

          <FormControl
            sx={{ flex: "0 1 10rem", minWidth: 0, maxWidth: "10rem" }}
          >
            <HabitStackSelectSingle
              name={constructFieldName(props.namePrefix, "stack")}
              label="Stack"
              allowNone
              allStacks={(props.allStacks ?? []).filter(
                (stack) => stack.period === selectedPeriod,
              )}
              value={selectedStackRefId}
              defaultValue={props.habit.stack_ref_id}
              inputsEnabled={props.inputsEnabled}
              onChange={(value) => setSelectedStackRefId(value)}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/stack_ref_id"
            />
          </FormControl>

          <FormControl sx={{ flex: "0 0 auto" }}>
            <IsKeySelect
              name={constructFieldName(props.namePrefix, "isKey")}
              defaultValue={props.habit.is_key}
              inputsEnabled={props.inputsEnabled}
            />
            <FieldError actionResult={props.actionData} fieldName="/is_key" />
          </FormControl>
        </Stack>

        <Stack
          direction={isBigScreen ? "row" : "column"}
          useFlexGap
          spacing={1}
        >
          <FormControl fullWidth sx={{ flexGrow: 2, minWidth: 0 }}>
            <TagsEditor
              name="tags"
              aloneOnLine
              allTags={props.allTags}
              linkedTags={props.tags}
              defaultValue={props.tags.map((tag) => tag.ref_id)}
              inputsEnabled={props.inputsEnabled}
              entityOwnerRefId={props.entityOwner?.ref_id}
              owner={entityLinkStd(NamedEntityTag.HABIT, props.habit.ref_id)}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/tags_names"
            />
          </FormControl>

          <FormControl fullWidth sx={{ flexGrow: 2, minWidth: 0 }}>
            <ContactsEditor
              name="contacts_names"
              aloneOnLine
              allContacts={props.allContacts}
              linkedContacts={props.contacts}
              defaultValue={props.contacts.map((contact) => contact.ref_id)}
              inputsEnabled={props.inputsEnabled}
              entityOwnerRefId={props.entityOwner?.ref_id}
              owner={entityLinkStd(NamedEntityTag.HABIT, props.habit.ref_id)}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/contacts_names"
            />
          </FormControl>

          <FormControl fullWidth sx={{ flexGrow: 2, minWidth: 0 }}>
            <LocationsEditor
              name="locations"
              aloneOnLine
              linkedLocation={props.location}
              inputsEnabled={props.inputsEnabled}
              entityOwnerRefId={props.entityOwner?.ref_id}
              owner={entityLinkStd(NamedEntityTag.HABIT, props.habit.ref_id)}
            />
          </FormControl>
        </Stack>

        {isWorkspaceFeatureAvailable(
          props.topLevelInfo.workspace,
          WorkspaceFeature.LIFE_PLAN,
        ) && (
          <FormControl fullWidth>
            <LifePlanAssociations
              inputsEnabled={
                props.inputsEnabled && lifePlanAssociationsInWorkspace
              }
              aspectName={constructFieldName(props.namePrefix, "aspect")}
              chapterName={constructFieldName(props.namePrefix, "chapter")}
              goalName={constructFieldName(props.namePrefix, "goal")}
              allAspects={allAspects}
              aspectValue={selectedAspectRefId}
              onAspectChange={setSelectedAspectRefId}
              aspectDefaultValue={props.habit.aspect_ref_id}
              allChapters={allChapters}
              chapterDefaultValue={props.habit.chapter_ref_id}
              allGoals={allGoals}
              goalDefaultValue={props.habit.goal_ref_id}
              birthday={birthdayDate!}
              today={aDateToDate(props.topLevelInfo.today)}
              allMilestones={props.allMilestones}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/aspect_ref_id"
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/chapter_ref_id"
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/goal_ref_id"
            />
          </FormControl>
        )}

        <RecurringTaskGenParamsBlock
          inputsEnabled={props.inputsEnabled}
          allowSkipRule
          namePrefix={props.namePrefix}
          period={selectedPeriod}
          allowPeriodChange={false}
          onChangePeriod={(newPeriod) => {
            if (newPeriod === "none") {
              setSelectedPeriod(RecurringTaskPeriod.DAILY);
            } else {
              setSelectedPeriod(newPeriod);
            }
            const nextPeriod =
              newPeriod === "none" ? RecurringTaskPeriod.DAILY : newPeriod;
            const selectedStack = (props.allStacks ?? []).find(
              (stack) => stack.ref_id === selectedStackRefId,
            );
            if (selectedStack && selectedStack.period !== nextPeriod) {
              setSelectedStackRefId(undefined);
            }
          }}
          eisen={props.habit.gen_params.eisen}
          difficulty={props.habit.gen_params.difficulty}
          actionableFromDay={props.habit.gen_params.actionable_from_day}
          actionableFromMonth={props.habit.gen_params.actionable_from_month}
          dueAtDay={props.habit.gen_params.due_at_day}
          dueAtMonth={props.habit.gen_params.due_at_month}
          skipRule={props.habit.gen_params.skip_rule}
          actionData={props.actionData}
        />

        <SchedulingParamsBlock
          inputsEnabled={props.inputsEnabled}
          namePrefix={props.namePrefix}
          schedulingParams={props.habit.scheduling_params}
          actionData={props.actionData}
        />

        {selectedPeriod !== RecurringTaskPeriod.DAILY && (
          <Stack direction="row" spacing={2}>
            <FormControl sx={{ flexGrow: 3 }}>
              <HabitRepeatStrategySelect
                name={constructFieldName(props.namePrefix, "repeatsStrategy")}
                inputsEnabled={props.inputsEnabled}
                allowNone
                value={selectedRepeatsStrategy}
                onChange={(newStrategy) =>
                  setSelectedRepeatsStrategy(newStrategy)
                }
              />
              <FieldError
                actionResult={props.actionData}
                fieldName="/repeats_strategy"
              />
            </FormControl>

            {selectedRepeatsStrategy !== "none" && (
              <FormControl sx={{ flexGrow: 1 }}>
                <InputLabel id="repeatsInPeriodCount">
                  Repeats In Period [Optional]
                </InputLabel>
                <OutlinedInput
                  label="Repeats In Period"
                  name={constructFieldName(
                    props.namePrefix,
                    "repeatsInPeriodCount",
                  )}
                  readOnly={!props.inputsEnabled}
                  disabled={!props.inputsEnabled}
                  defaultValue={props.habit.repeats_in_period_count}
                  sx={{ height: "100%" }}
                />
                <FieldError
                  actionResult={props.actionData}
                  fieldName="/repeats_in_period_count"
                />
              </FormControl>
            )}
          </Stack>
        )}

        <FormControl fullWidth>
          <FormControlLabel
            control={
              <Switch
                name={constructFieldName(props.namePrefix, "suspended")}
                readOnly={!props.inputsEnabled}
                disabled={!props.inputsEnabled}
                defaultChecked={props.habit.suspended}
              />
            }
            label="Suspended"
          />
          <FieldError actionResult={props.actionData} fieldName="/suspended" />
        </FormControl>
      </SectionCard>
      <EntityLocationMapSection location={props.location} />
    </>
  );
}

function constructIntentName(
  intentPrefix: string | undefined,
  intent: string,
): string {
  if (!intentPrefix) {
    return intent;
  }
  return `${intentPrefix}-${intent}`;
}

function mergeForeignAspectSummary(
  allAspects: AspectSummary[],
  aspect: Aspect | null | undefined,
  aspectRefId: string,
): AspectSummary[] {
  if (allAspects.some((entry) => entry.ref_id === aspectRefId)) {
    return allAspects;
  }
  if (
    aspect === undefined ||
    aspect === null ||
    aspect.ref_id !== aspectRefId
  ) {
    return allAspects;
  }
  // Detach from the foreign parent chain so tree helpers can still render it.
  return [
    ...allAspects,
    {
      ref_id: aspect.ref_id,
      parent_aspect_ref_id: null,
      name: aspect.name,
      order_of_child_aspects: [],
    },
  ];
}

function mergeForeignChapterSummary(
  allChapters: ChapterSummary[],
  chapter: Chapter | null | undefined,
  chapterRefId: string | null | undefined,
): ChapterSummary[] {
  if (
    chapterRefId === undefined ||
    chapterRefId === null ||
    allChapters.some((entry) => entry.ref_id === chapterRefId)
  ) {
    return allChapters;
  }
  if (
    chapter === undefined ||
    chapter === null ||
    chapter.ref_id !== chapterRefId
  ) {
    return allChapters;
  }
  return [
    ...allChapters,
    {
      ref_id: chapter.ref_id,
      name: chapter.name,
      start_date: chapter.start_date,
      end_date: chapter.end_date,
      aspect_ref_id: chapter.aspect_ref_id,
    },
  ];
}

function mergeForeignGoalSummary(
  allGoals: GoalSummary[],
  goal: Goal | null | undefined,
  goalRefId: string | null | undefined,
): GoalSummary[] {
  if (
    goalRefId === undefined ||
    goalRefId === null ||
    allGoals.some((entry) => entry.ref_id === goalRefId)
  ) {
    return allGoals;
  }
  if (goal === undefined || goal === null || goal.ref_id !== goalRefId) {
    return allGoals;
  }
  return [
    ...allGoals,
    {
      ref_id: goal.ref_id,
      name: goal.name,
      aspect_ref_id: goal.aspect_ref_id,
      parent_goal_ref_id: goal.parent_goal_ref_id,
    },
  ];
}
