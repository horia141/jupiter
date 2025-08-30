import type {
  BigPlanSummary,
  InboxTask,
  InboxTaskLoadResult,
  ProjectSummary,
} from "@jupiter/webapi-client";
import {
  InboxTaskSource,
  InboxTaskStatus,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import LaunchIcon from "@mui/icons-material/Launch";
import {
  Autocomplete,
  Box,
  Button,
  ButtonGroup,
  CardActions,
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import type { SomeErrorNoData } from "~/logic/action-result";
import { isInboxTaskCoreFieldEditable } from "~/logic/domain/inbox-task";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";
import { DifficultySelect } from "~/components/domain/core/difficulty-select";
import { EisenhowerSelect } from "~/components/domain/core/eisenhower-select";
import { InboxTaskSourceLink } from "~/components/domain/concept/inbox-task/inbox-task-source-link";
import { InboxTaskStatusBigTag } from "~/components/domain/concept/inbox-task/inbox-task-status-big-tag";
import { FieldError } from "~/components/infra/errors";
import {
  ActionSingle,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { ProjectSelect } from "~/components/domain/concept/project/project-select";
import { IsKeySelect } from "~/components/domain/core/is-key-select";
import {
  constructFieldErrorName,
  constructFieldName,
} from "~/logic/field-names";
import { DateInputWithSuggestions } from "~/components/domain/core/date-input-with-suggestions";
import {
  getSuggestedDatesForInboxTaskActionableDate,
  getSuggestedDatesForInboxTaskDueDate,
} from "~/logic/domain/suggested-date";

interface InboxTaskPropertiesEditorProps {
  title: string;
  showLinkToInboxTask?: boolean;
  intentPrefix?: string;
  namePrefix?: string;
  fieldsPrefix?: string;
  topLevelInfo: TopLevelInfo;
  rootProject: ProjectSummary;
  allProjects: ProjectSummary[];
  allBigPlans: BigPlanSummary[];
  inputsEnabled: boolean;
  inboxTask: InboxTask;
  inboxTaskInfo: InboxTaskLoadResult;
  actionData?: SomeErrorNoData;
}

type BigPlanACOption = {
  label: string;
  big_plan_id: string;
};

export function InboxTaskPropertiesEditor(
  props: InboxTaskPropertiesEditorProps,
) {
  const [selectedBigPlan, setSelectedBigPlan] = useState(
    props.inboxTaskInfo.big_plan
      ? {
          label: props.inboxTaskInfo.big_plan.name,
          big_plan_id: props.inboxTaskInfo.big_plan.ref_id,
        }
      : {
          label: "None",
          big_plan_id: "none",
        },
  );

  const [selectedProject, setSelectedProject] = useState(
    props.inboxTaskInfo.project.ref_id,
  );
  const [blockedToSelectProject, setBlockedToSelectProject] = useState(
    props.inboxTask.source === InboxTaskSource.BIG_PLAN,
  );
  const corePropertyEditable = isInboxTaskCoreFieldEditable(
    props.inboxTask.source,
  );

  const allProjectsById: { [k: string]: ProjectSummary } = {};
  if (
    isWorkspaceFeatureAvailable(
      props.topLevelInfo.workspace,
      WorkspaceFeature.PROJECTS,
    )
  ) {
    for (const project of props.allProjects) {
      allProjectsById[project.ref_id] = project;
    }
  }

  const allBigPlansById: { [k: string]: BigPlanSummary } = {};
  let allBigPlansAsOptions: Array<{ label: string; big_plan_id: string }> = [];

  if (
    isWorkspaceFeatureAvailable(
      props.topLevelInfo.workspace,
      WorkspaceFeature.BIG_PLANS,
    )
  ) {
    for (const bigPlan of props.allBigPlans) {
      allBigPlansById[bigPlan.ref_id] = bigPlan;
    }

    allBigPlansAsOptions = [
      {
        label: "None",
        big_plan_id: "none",
      },
    ].concat(
      props.allBigPlans.map((bp: BigPlanSummary) => ({
        label: bp.name,
        big_plan_id: bp.ref_id,
      })),
    );
  }

  function handleChangeBigPlan(
    e: React.SyntheticEvent,
    { label, big_plan_id }: BigPlanACOption,
  ) {
    setSelectedBigPlan({ label, big_plan_id });
    if (big_plan_id === "none") {
      setSelectedProject(props.rootProject.ref_id);
      setBlockedToSelectProject(false);
    } else {
      const projectId = allBigPlansById[big_plan_id].project_ref_id;
      const projectKey = allProjectsById[projectId].ref_id;
      setSelectedProject(projectKey);
      setBlockedToSelectProject(true);
    }
  }

  useEffect(() => {
    // Update states based on loader data. This is necessary because these
    // two are not otherwise updated when the loader data changes. Which happens
    // on a navigation event.
    setSelectedBigPlan(
      props.inboxTaskInfo.big_plan
        ? {
            label: props.inboxTaskInfo.big_plan.name,
            big_plan_id: props.inboxTaskInfo.big_plan.ref_id,
          }
        : {
            label: "None",
            big_plan_id: "none",
          },
    );

    setSelectedProject(props.inboxTaskInfo.project.ref_id);
  }, [props.inboxTaskInfo]);

  return (
    <SectionCard
      title={props.title}
      actions={
        <SectionActions
          id="inbox-task-editor"
          topLevelInfo={props.topLevelInfo}
          inputsEnabled={props.inputsEnabled}
          actions={
            props.showLinkToInboxTask
              ? [
                  NavSingle({
                    text: "Inbox Task",
                    icon: <LaunchIcon />,
                    link: `/app/workspace/inbox-tasks/${props.inboxTask.ref_id}`,
                  }),
                  ActionSingle({
                    id: "inbox-task-editor-save",
                    text: "Save",
                    value: constructIntentName(props.intentPrefix, "update"),
                    highlight: true,
                  }),
                ]
              : [
                  ActionSingle({
                    id: "inbox-task-editor-save",
                    text: "Save",
                    value: constructIntentName(props.intentPrefix, "update"),
                    highlight: true,
                  }),
                ]
          }
        />
      }
    >
      <Stack spacing={2} useFlexGap>
        <Box sx={{ display: "flex", flexDirection: "row", gap: "0.25rem" }}>
          <input
            type="hidden"
            name={constructFieldName(props.namePrefix, "refId")}
            value={props.inboxTask.ref_id}
          />
          <FormControl sx={{ flexGrow: 3 }}>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput
              label="Name"
              name={constructFieldName(props.namePrefix, "name")}
              readOnly={!props.inputsEnabled || !corePropertyEditable}
              defaultValue={props.inboxTask.name}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName={constructFieldErrorName(props.fieldsPrefix, "name")}
            />
            <input
              type="hidden"
              name={constructFieldName(props.namePrefix, "source")}
              value={props.inboxTask.source}
            />
          </FormControl>
          <FormControl sx={{ flexGrow: 1 }}>
            <IsKeySelect
              name={constructFieldName(props.namePrefix, "isKey")}
              defaultValue={props.inboxTask.is_key}
              inputsEnabled={props.inputsEnabled && corePropertyEditable}
            />
          </FormControl>
          <FormControl sx={{ flexGrow: 1 }}>
            <InboxTaskStatusBigTag status={props.inboxTask.status} />
            <input
              type="hidden"
              name={constructFieldName(props.namePrefix, "status")}
              value={props.inboxTask.status}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName={constructFieldErrorName(props.fieldsPrefix, "status")}
            />
          </FormControl>
          <InboxTaskSourceLink inboxTaskResult={props.inboxTaskInfo} />
        </Box>

        {isWorkspaceFeatureAvailable(
          props.topLevelInfo.workspace,
          WorkspaceFeature.BIG_PLANS,
        ) &&
          (props.inboxTask.source === InboxTaskSource.USER ||
            props.inboxTask.source === InboxTaskSource.BIG_PLAN) && (
            <>
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  autoHighlight
                  id="bigPlan"
                  options={allBigPlansAsOptions}
                  readOnly={!props.inputsEnabled}
                  value={selectedBigPlan}
                  disableClearable={true}
                  onChange={handleChangeBigPlan}
                  isOptionEqualToValue={(o, v) =>
                    o.big_plan_id === v.big_plan_id
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Big Plan" />
                  )}
                />

                <FieldError
                  actionResult={props.actionData}
                  fieldName={constructFieldErrorName(
                    props.fieldsPrefix,
                    "big_plan_ref_id",
                  )}
                />

                <input
                  type="hidden"
                  name={constructFieldName(props.namePrefix, "bigPlan")}
                  value={selectedBigPlan.big_plan_id}
                />
              </FormControl>
            </>
          )}

        {isWorkspaceFeatureAvailable(
          props.topLevelInfo.workspace,
          WorkspaceFeature.PROJECTS,
        ) && (
          <FormControl fullWidth>
            <ProjectSelect
              name={constructFieldName(props.namePrefix, "project")}
              label="Project"
              inputsEnabled={props.inputsEnabled && corePropertyEditable}
              disabled={!corePropertyEditable || blockedToSelectProject}
              allProjects={props.allProjects}
              value={selectedProject}
              onChange={setSelectedProject}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName={constructFieldErrorName(
                props.fieldsPrefix,
                "project_ref_id",
              )}
            />
          </FormControl>
        )}

        <FormControl fullWidth>
          <FormLabel id="eisen">Eisenhower</FormLabel>
          <EisenhowerSelect
            name={constructFieldName(props.namePrefix, "eisen")}
            inputsEnabled={props.inputsEnabled && corePropertyEditable}
            defaultValue={props.inboxTask.eisen}
          />
          <FieldError
            actionResult={props.actionData}
            fieldName={constructFieldErrorName(props.fieldsPrefix, "eisen")}
          />
        </FormControl>

        <FormControl fullWidth>
          <FormLabel id="difficulty">Difficulty</FormLabel>
          <DifficultySelect
            name={constructFieldName(props.namePrefix, "difficulty")}
            inputsEnabled={props.inputsEnabled && corePropertyEditable}
            defaultValue={props.inboxTask.difficulty}
          />
          <FieldError
            actionResult={props.actionData}
            fieldName={constructFieldErrorName(
              props.fieldsPrefix,
              "difficulty",
            )}
          />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="actionableDate" shrink>
            Actionable From {corePropertyEditable ? "[Optional]" : ""}
          </InputLabel>
          <DateInputWithSuggestions
            name={constructFieldName(props.namePrefix, "actionableDate")}
            label="actionableDate"
            inputsEnabled={props.inputsEnabled && corePropertyEditable}
            defaultValue={props.inboxTask.actionable_date}
            suggestedDates={getSuggestedDatesForInboxTaskActionableDate(
              props.topLevelInfo.today,
              props.inboxTaskInfo.big_plan,
              props.inboxTaskInfo.time_plan,
            )}
          />

          <FieldError
            actionResult={props.actionData}
            fieldName={constructFieldErrorName(
              props.fieldsPrefix,
              "actionable_date",
            )}
          />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="dueDate" shrink margin="dense">
            Due At {corePropertyEditable ? "[Optional]" : ""}
          </InputLabel>
          <DateInputWithSuggestions
            name={constructFieldName(props.namePrefix, "dueDate")}
            label="dueDate"
            inputsEnabled={props.inputsEnabled && corePropertyEditable}
            defaultValue={props.inboxTask.due_date}
            suggestedDates={getSuggestedDatesForInboxTaskDueDate(
              props.topLevelInfo.today,
              props.inboxTaskInfo.big_plan,
              props.inboxTaskInfo.time_plan,
            )}
          />

          <FieldError
            actionResult={props.actionData}
            fieldName={constructFieldErrorName(props.fieldsPrefix, "due_date")}
          />
        </FormControl>
      </Stack>

      <CardActions sx={{ paddingLeft: "0px", paddingRight: "0px" }}>
        <Stack direction="column" spacing={1} sx={{ width: "100%" }}>
          {(props.inboxTask.status === InboxTaskStatus.NOT_STARTED ||
            props.inboxTask.status === InboxTaskStatus.NOT_STARTED_GEN) && (
            <ButtonGroup fullWidth>
              <Button
                size="small"
                variant="contained"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "mark-done")}
              >
                Mark Done
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "mark-not-done")}
              >
                Mark Not Done
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "start")}
              >
                Start
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "block")}
              >
                Block
              </Button>
            </ButtonGroup>
          )}

          {props.inboxTask.status === InboxTaskStatus.IN_PROGRESS && (
            <ButtonGroup fullWidth>
              <Button
                size="small"
                variant="contained"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "mark-done")}
              >
                Mark Done
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "mark-not-done")}
              >
                Mark Not Done
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "block")}
              >
                Block
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "stop")}
              >
                Stop
              </Button>
            </ButtonGroup>
          )}

          {props.inboxTask.status === InboxTaskStatus.BLOCKED && (
            <ButtonGroup fullWidth>
              <Button
                size="small"
                variant="contained"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "mark-done")}
              >
                Mark Done
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "mark-not-done")}
              >
                Mark Not Done
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "restart")}
              >
                Restart
              </Button>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "stop")}
              >
                Stop
              </Button>
            </ButtonGroup>
          )}

          {(props.inboxTask.status === InboxTaskStatus.DONE ||
            props.inboxTask.status === InboxTaskStatus.NOT_DONE) && (
            <ButtonGroup fullWidth>
              <Button
                size="small"
                variant="outlined"
                disabled={!props.inputsEnabled}
                type="submit"
                name="intent"
                value={constructIntentName(props.intentPrefix, "reactivate")}
              >
                Reactivate
              </Button>
            </ButtonGroup>
          )}
        </Stack>
      </CardActions>
    </SectionCard>
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
