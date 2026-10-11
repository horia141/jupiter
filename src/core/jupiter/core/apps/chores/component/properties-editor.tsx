import type {
  Aspect,
  AspectSummary,
  Chapter,
  ChapterSummary,
  Chore,
  ChoreStack,
  Contact,
  Goal,
  GoalSummary,
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
import { ChoreStackSelectSingle } from "#/core/apps/chores/component/stack-select-single";
import { ContactsEditor } from "#/core/common/sub/contacts/component/contacts-editor";
import { EntityLocationMapSection } from "#/core/common/sub/locations/component/entity-location-map-section";
import { LocationsEditor } from "#/core/common/sub/locations/component/locations-editor";
import { TagsEditor } from "#/core/common/sub/tags/component/tags-editor";
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

interface ChorePropertiesEditorProps {
  title: string;
  showLinkToChore?: boolean;
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
  chore: Chore;
  allStacks?: ChoreStack[];
  actionData?: SomeErrorNoData;
}

export function ChorePropertiesEditor(props: ChorePropertiesEditorProps) {
  const isBigScreen = useBigScreen();
  const birthdayDate = props.lifePlan
    ? lifePlanBirthdayDate(props.lifePlan)
    : null;
  const [selectedAspectRefId, setSelectedAspectRefId] = useState(
    props.chore.aspect_ref_id,
  );
  const [selectedPeriod, setSelectedPeriod] = useState(
    props.chore.gen_params.period,
  );
  const [selectedStackRefId, setSelectedStackRefId] = useState<
    string | undefined
  >(props.chore.stack_ref_id ?? undefined);
  const showGen = props.showGen ?? true;

  // Shared chores may reference life-plan entities from another workspace.
  // Include those for display, but keep associations read-only.
  const lifePlanAssociationsInWorkspace = props.allAspects.some(
    (aspect) => aspect.ref_id === props.chore.aspect_ref_id,
  );
  const allAspects = useMemo(
    () =>
      mergeForeignAspectSummary(
        props.allAspects,
        props.aspect,
        props.chore.aspect_ref_id,
      ),
    [props.allAspects, props.aspect, props.chore.aspect_ref_id],
  );
  const allChapters = useMemo(
    () =>
      mergeForeignChapterSummary(
        props.allChapters,
        props.chapter,
        props.chore.chapter_ref_id,
      ),
    [props.allChapters, props.chapter, props.chore.chapter_ref_id],
  );
  const allGoals = useMemo(
    () =>
      mergeForeignGoalSummary(
        props.allGoals,
        props.goal,
        props.chore.goal_ref_id,
      ),
    [props.allGoals, props.goal, props.chore.goal_ref_id],
  );

  return (
    <>
      <SectionCard
        title={props.title}
        actions={
          <SectionActions
            id="chore-properties"
            topLevelInfo={props.topLevelInfo}
            inputsEnabled={props.inputsEnabled}
            actions={[
              ActionSingle({
                id: "chore-update",
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
              props.showLinkToChore
                ? [
                    NavSingle({
                      text: "Chore",
                      link: `/app/workspace/apps/chores/chores/${props.chore.ref_id}`,
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
          value={props.chore.ref_id}
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
              defaultValue={props.chore.name}
            />
            <FieldError actionResult={props.actionData} fieldName="/name" />
          </FormControl>

          <FormControl
            sx={{ flex: "0 1 10rem", minWidth: 0, maxWidth: "10rem" }}
          >
            <ChoreStackSelectSingle
              name={constructFieldName(props.namePrefix, "stack")}
              label="Stack"
              allowNone
              allStacks={(props.allStacks ?? []).filter(
                (stack) => stack.period === selectedPeriod,
              )}
              value={selectedStackRefId}
              defaultValue={props.chore.stack_ref_id}
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
              defaultValue={props.chore.is_key}
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
              owner={entityLinkStd(NamedEntityTag.CHORE, props.chore.ref_id)}
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
              owner={entityLinkStd(NamedEntityTag.CHORE, props.chore.ref_id)}
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
              owner={entityLinkStd(NamedEntityTag.CHORE, props.chore.ref_id)}
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
              aspectDefaultValue={props.chore.aspect_ref_id}
              allChapters={allChapters}
              chapterDefaultValue={props.chore.chapter_ref_id}
              allGoals={allGoals}
              goalDefaultValue={props.chore.goal_ref_id}
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
          eisen={props.chore.gen_params.eisen}
          difficulty={props.chore.gen_params.difficulty}
          actionableFromDay={props.chore.gen_params.actionable_from_day}
          actionableFromMonth={props.chore.gen_params.actionable_from_month}
          dueAtDay={props.chore.gen_params.due_at_day}
          dueAtMonth={props.chore.gen_params.due_at_month}
          skipRule={props.chore.gen_params.skip_rule}
          actionData={props.actionData}
        />

        <SchedulingParamsBlock
          inputsEnabled={props.inputsEnabled}
          namePrefix={props.namePrefix}
          schedulingParams={props.chore.scheduling_params}
          actionData={props.actionData}
        />

        <FormControl fullWidth>
          <FormControlLabel
            control={
              <Switch
                name={constructFieldName(props.namePrefix, "mustDo")}
                readOnly={!props.inputsEnabled}
                disabled={!props.inputsEnabled}
                defaultChecked={props.chore.must_do}
              />
            }
            label="Must Do In Vacation"
          />
          <FieldError actionResult={props.actionData} fieldName="/must_do" />
        </FormControl>

        <FormControl fullWidth>
          <FormControlLabel
            control={
              <Switch
                name={constructFieldName(props.namePrefix, "suspended")}
                readOnly={!props.inputsEnabled}
                disabled={!props.inputsEnabled}
                defaultChecked={props.chore.suspended}
              />
            }
            label="Suspended"
          />
          <FieldError actionResult={props.actionData} fieldName="/suspended" />
        </FormControl>

        <Stack spacing={2} direction={isBigScreen ? "row" : "column"}>
          <FormControl fullWidth>
            <InputLabel id="startAtDate" shrink>
              Start At Date [Optional]
            </InputLabel>
            <OutlinedInput
              type="date"
              notched
              label="startAtDate"
              name={constructFieldName(props.namePrefix, "startAtDate")}
              readOnly={!props.inputsEnabled}
              disabled={!props.inputsEnabled}
              defaultValue={
                props.chore.start_at_date
                  ? aDateToDate(props.chore.start_at_date).toFormat(
                      "yyyy-MM-dd",
                    )
                  : undefined
              }
            />
            <FieldError
              actionResult={props.actionData}
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
              name={constructFieldName(props.namePrefix, "endAtDate")}
              readOnly={!props.inputsEnabled}
              disabled={!props.inputsEnabled}
              defaultValue={
                props.chore.end_at_date
                  ? aDateToDate(props.chore.end_at_date).toFormat("yyyy-MM-dd")
                  : undefined
              }
            />
            <FieldError
              actionResult={props.actionData}
              fieldName="/end_at_date"
            />
          </FormControl>
        </Stack>
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
