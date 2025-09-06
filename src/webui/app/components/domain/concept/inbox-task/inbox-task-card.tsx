import type {
  ADate,
  BigPlan,
  Chore,
  EmailTask,
  Habit,
  InboxTask,
  InboxTaskStatus,
  Metric,
  Person,
  SlackTask,
} from "@jupiter/webapi-client";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DeleteIcon from "@mui/icons-material/Delete";
import type { ChipProps } from "@mui/material";
import {
  Box,
  Card,
  CardActions,
  CardContent,
  Chip,
  IconButton,
  styled,
  useTheme,
} from "@mui/material";
import type { PanInfo } from "framer-motion";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { useContext, useState } from "react";

import { ClientOnly } from "~/components/infra/client-only";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { aDateToDate } from "~/logic/domain/adate";
import type {
  InboxTaskOptimisticState,
  InboxTaskParent,
} from "~/logic/domain/inbox-task";
import { isCompleted } from "~/logic/domain/inbox-task-status";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { useBigScreen } from "~/rendering/use-big-screen";
import type { TopLevelInfo } from "~/top-level-context";
import { ADateTag } from "~/components/domain/core/adate-tag";
import { BigPlanTag } from "~/components/domain/concept/big-plan/big-plan-tag";
import { ChoreTag } from "~/components/domain/concept/chore/chore-tag";
import { DifficultyTag } from "~/components/domain/core/difficulty-tag";
import { EisenTag } from "~/components/domain/core/eisen-tag";
import { EmailTaskTag } from "~/components/domain/concept/email-task/email-task-tag";
import { EntityNameComponent } from "~/components/infra/entity-name";
import { HabitTag } from "~/components/domain/concept/habit/habit-tag";
import { InboxTaskSourceTag } from "~/components/domain/concept/inbox-task/inbox-task-source-tag";
import { InboxTaskStatusTag } from "~/components/domain/concept/inbox-task/inbox-task-status-tag";
import { EntityLink } from "~/components/infra/entity-card";
import { MetricTag } from "~/components/domain/concept/metric/metric-tag";
import { PersonTag } from "~/components/domain/concept/person/person-tag";
import { ProjectTag } from "~/components/domain/concept/project/project-tag";
import { SlackTaskTag } from "~/components/domain/concept/slack-task/slack-task-tag";
import { IsKeyTag } from "~/components/domain/core/is-key-tag";

export interface InboxTaskShowOptions {
  showStatus?: boolean;
  showSource?: boolean;
  showProject?: boolean;
  showEisen?: boolean;
  showDifficulty?: boolean;
  showActionableDate?: boolean;
  showDueDate?: boolean;
  showParent?: boolean;
  showHandleMarkDone?: boolean;
  showHandleMarkNotDone?: boolean;
}

export interface InboxTaskCardProps {
  topLevelInfo: TopLevelInfo;
  compact?: boolean;
  allowSwipe?: boolean;
  allowSelect?: boolean;
  selected?: boolean;
  showOptions: InboxTaskShowOptions;
  inboxTask: InboxTask;
  optimisticState?: InboxTaskOptimisticState;
  parent?: InboxTaskParent;
  onClick?: (it: InboxTask) => void;
  onMarkDone?: (it: InboxTask) => void;
  onMarkNotDone?: (it: InboxTask) => void;
}

const SWIPE_THRESHOLD = 200;
const SWIPE_COMPLETE_THRESHOLD = 150;

export function InboxTaskCard(props: InboxTaskCardProps) {
  const isBigScreen = useBigScreen();
  const theme = useTheme();

  const [handlerInProgress, setHandlerInProgress] = useState(false);

  function markDoneHandler() {
    setHandlerInProgress(true);
    setTimeout(() => {
      if (props.onMarkDone) {
        props.onMarkDone(props.inboxTask);
      }
      setHandlerInProgress(false);
    }, 0);
  }

  function markNotDoneHandler() {
    setHandlerInProgress(true);
    setTimeout(() => {
      if (props.onMarkNotDone) {
        props.onMarkNotDone(props.inboxTask);
      }
      setHandlerInProgress(false);
    }, 0);
  }

  function onDragEnd(
    event: MouseEvent | TouchEvent | PointerEvent,
    info: PanInfo,
  ) {
    if (info.offset.x < -SWIPE_COMPLETE_THRESHOLD) {
      setTimeout(() => {
        if (props.onMarkDone) {
          props.onMarkDone(props.inboxTask);
        }
      }, 0);
    } else if (info.offset.x < SWIPE_COMPLETE_THRESHOLD) {
      // do nothing
    } else {
      setTimeout(() => {
        if (props.onMarkNotDone) {
          props.onMarkNotDone(props.inboxTask);
        }
      }, 0);
    }
  }

  const x = useMotionValue(0);
  const background = useTransform(
    x,
    [-SWIPE_COMPLETE_THRESHOLD, 0, SWIPE_COMPLETE_THRESHOLD],
    [
      theme.palette.success.light,
      theme.palette.background.paper,
      theme.palette.warning.light,
    ],
  );

  const inputsEnabled =
    props.inboxTask.archived === false && !handlerInProgress;

  return (
    <motion.div
      drag={inputsEnabled && props.allowSwipe ? "x" : false}
      whileDrag={{ scale: 1.1 }}
      dragSnapToOrigin={true}
      dragElastic={0.1}
      dragConstraints={{ left: -SWIPE_THRESHOLD, right: SWIPE_THRESHOLD }}
      onDragEnd={onDragEnd}
      style={{ x, background }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, height: "0px", marginTop: "0px" }}
      transition={{ duration: 1 }}
    >
      <StyledCard
        id={`inbox-task-${props.inboxTask.ref_id}`}
        isselected={((props.allowSelect && props.selected) || false).toString()}
        enabled={inputsEnabled.toString()}
        onClick={() => props.onClick && props.onClick(props.inboxTask)}
      >
        <OverdueWarning
          today={props.topLevelInfo.today}
          status={props.inboxTask.status}
          dueDate={props.inboxTask.due_date}
        />
        <CardContent
          sx={{
            paddingTop: isBigScreen ? "0.5rem" : "1rem",
            paddingLeft: "0.5rem",
            paddingBottom: "0.5rem",
          }}
        >
          <EntityLink
            to={`/app/workspace/inbox-tasks/${props.inboxTask.ref_id}`}
            block={props.onClick !== undefined}
            inline
          >
            <IsKeyTag isKey={props.inboxTask.is_key} />
            <EntityNameComponent
              compact={props.compact}
              name={props.inboxTask.name}
            />
          </EntityLink>
          <TagsContained>
            {props.showOptions.showStatus && (
              <InboxTaskStatusTag
                status={props.optimisticState?.status ?? props.inboxTask.status}
              />
            )}
            {props.showOptions.showSource && (
              <InboxTaskSourceTag source={props.inboxTask.source} />
            )}
            {isWorkspaceFeatureAvailable(
              props.topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS,
            ) &&
              props.showOptions.showProject &&
              props.parent?.project && (
                <ProjectTag project={props.parent?.project} />
              )}
            {props.showOptions.showEisen && (
              <EisenTag
                eisen={props.optimisticState?.eisen ?? props.inboxTask.eisen}
              />
            )}
            {props.showOptions.showDifficulty && (
              <DifficultyTag difficulty={props.inboxTask.difficulty} />
            )}
            {props.showOptions.showActionableDate &&
              props.inboxTask.actionable_date && (
                <ADateTag
                  label="Actionable from"
                  date={props.inboxTask.actionable_date}
                />
              )}
            {props.showOptions.showDueDate && props.inboxTask.due_date && (
              <ADateTag label="Due at" date={props.inboxTask.due_date} />
            )}
            {props.showOptions.showParent && (
              <>
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.BIG_PLANS,
                ) &&
                  props.parent &&
                  props.parent.bigPlan && (
                    <BigPlanTag bigPlan={props.parent.bigPlan as BigPlan} />
                  )}
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.HABITS,
                ) &&
                  props.parent &&
                  props.parent.habit && (
                    <HabitTag habit={props.parent.habit as Habit} />
                  )}
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.CHORES,
                ) &&
                  props.parent &&
                  props.parent.chore && (
                    <ChoreTag chore={props.parent.chore as Chore} />
                  )}
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.METRICS,
                ) &&
                  props.parent &&
                  props.parent.metric && (
                    <MetricTag metric={props.parent.metric as Metric} />
                  )}
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.PERSONS,
                ) &&
                  props.parent &&
                  props.parent.person && (
                    <PersonTag person={props.parent.person as Person} />
                  )}
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.SLACK_TASKS,
                ) &&
                  props.parent &&
                  props.parent.slackTask && (
                    <SlackTaskTag
                      slackTask={props.parent.slackTask as SlackTask}
                    />
                  )}
                {isWorkspaceFeatureAvailable(
                  props.topLevelInfo.workspace,
                  WorkspaceFeature.EMAIL_TASKS,
                ) &&
                  props.parent &&
                  props.parent.emailTask && (
                    <EmailTaskTag
                      emailTask={props.parent.emailTask as EmailTask}
                    />
                  )}
              </>
            )}
          </TagsContained>
        </CardContent>
        {isBigScreen &&
          (props.showOptions.showHandleMarkDone ||
            props.showOptions.showHandleMarkNotDone) && (
            <CardActions
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-end",
              }}
            >
              {props.showOptions.showHandleMarkDone && (
                <IconButton
                  disabled={!inputsEnabled}
                  size="medium"
                  color="success"
                  onClick={markDoneHandler}
                >
                  <CheckCircleIcon fontSize="medium" />
                </IconButton>
              )}
              {props.showOptions.showHandleMarkNotDone && (
                <IconButton
                  disabled={!inputsEnabled}
                  size="medium"
                  color="warning"
                  onClick={markNotDoneHandler}
                >
                  <DeleteIcon fontSize="medium" />
                </IconButton>
              )}
            </CardActions>
          )}
      </StyledCard>
    </motion.div>
  );
}

interface StyledCardProps {
  enabled: string;
  isselected: string;
}

const StyledCard = styled(Card)<StyledCardProps>(
  ({ theme, enabled, isselected }) => ({
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    touchAction: "pan-y",
    position: "relative",
    boxShadow:
      isselected === "true"
        ? `inset 0 0 4px ${theme.palette.primary.main};`
        : undefined,
    backgroundColor:
      enabled === "true" ? "transparent" : theme.palette.action.hover,
  }),
);

const TagsContained = styled(Box)({
  display: "flex",
  flexDirection: "row",
  flexWrap: "wrap",
  gap: "0.25rem",
  paddingTop: "0.25rem",
});

interface OverdueWarningProps {
  today: ADate;
  status: InboxTaskStatus;
  dueDate?: ADate | null;
}

function OverdueWarning({ today, status, dueDate }: OverdueWarningProps) {
  const globalProperties = useContext(GlobalPropertiesContext);

  if (isCompleted(status)) {
    return null;
  }

  if (!dueDate) {
    return null;
  }

  const theToday = aDateToDate(today);
  const theDueDate = aDateToDate(dueDate);

  return (
    <ClientOnly fallback={<></>}>
      {() => {
        if (
          theDueDate <=
          theToday.minus({ days: globalProperties.overdueDangerDays })
        ) {
          return <OverdueWarningChip label="Overdue" color="error" />;
        } else if (
          theDueDate <=
          theToday.minus({ days: globalProperties.overdueWarningDays })
        ) {
          return <OverdueWarningChip label="Overdue" color="warning" />;
        } else if (
          theDueDate <=
          theToday.minus({ days: globalProperties.overdueInfoDays })
        ) {
          return <OverdueWarningChip label="Overdue" color="info" />;
        }
        return null;
      }}
    </ClientOnly>
  );
}

const OverdueWarningChip = styled(Chip)<ChipProps>(() => ({
  position: "absolute",
  top: "0px",
  fontSize: "0.75rem",
  height: "1rem",
  left: "0px",
  paddingTop: "0.05rem",
  paddingBottom: "0.05rem",
  paddingRight: "0.5rem",
  paddingLeft: "0.5rem",
  borderRadius: "0px",
  borderBottomRightRadius: "4px",
}));
