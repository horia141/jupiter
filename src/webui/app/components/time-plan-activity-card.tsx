import type { BigPlan, InboxTask, ProjectSummary, TimePlan, TimePlanActivity } from "@jupiter/webapi-client";
import { ApiError, RecurringTaskPeriod, TimePlanActivityTarget, WorkspaceFeature } from "@jupiter/webapi-client";
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
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Link,
  Outlet,
  useActionData,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { BigPlanStatusTag } from "~/components/big-plan-status-tag";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStatusTag } from "~/components/inbox-task-status-tag";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TimePlanActivityFeasabilityTag } from "~/components/time-plan-activity-feasability-tag";
import { TimePlanActivityKindTag } from "~/components/time-plan-activity-kind-tag";
import { TimePlanStack } from "~/components/time-plan-stack";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import { sortTimePlansNaturally } from "~/logic/domain/time-plan";
import { sortTimePlanActivitiesNaturally } from "~/logic/domain/time-plan-activity";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";

interface TimePlanActivityCardProps {
    topLevelInfo: TopLevelInfo;
    timePlan: TimePlan;
    activity: TimePlanActivity;
    inboxTasksByRefId: Map<string, InboxTask>;
    bigPlansByRefId: Map<string, BigPlan>;
    allowSelect?: boolean;
    selected?: boolean;
    onClick?: (activity: TimePlanActivity) => void;
  }
  
export  function TimePlanActivityCard(props: TimePlanActivityCardProps) {
    if (props.activity.target === TimePlanActivityTarget.INBOX_TASK) {
      const inboxTask = props.inboxTasksByRefId.get(props.activity.target_ref_id)!;
      return (
        <EntityCard 
            entityId={`time-plan-activity-${props.timePlan.ref_id}`}
            allowSelect={props.allowSelect}
            selected={props.selected}
            onClick={props.onClick ?? () => props.onClick(props.activity)}
            >
          <EntityLink
            to={`/workspace/time-plans/${props.timePlan.ref_id}/${props.activity.ref_id}`}
          >
            {inboxTask.name}
            <InboxTaskStatusTag status={inboxTask.status} />
            <TimePlanActivityKindTag kind={props.activity.kind} />
            <TimePlanActivityFeasabilityTag
              feasability={props.activity.feasability}
            />
          </EntityLink>
        </EntityCard>
      );
    } else if (isWorkspaceFeatureAvailable(props.topLevelInfo.workspace, WorkspaceFeature.BIG_PLANS)) {
      const bigPlan = props.bigPlansByRefId.get(props.activity.target_ref_id)!;
      return (
        <EntityCard 
            entityId={`time-plan-activity-${props.timePlan.ref_id}`}
            allowSelect={props.allowSelect}
            selected={props.selected}
            onClick={props.onClick ?? () => props.onClick(props.activity)}
        >
          <EntityLink
            to={`/workspace/time-plans/${props.timePlan.ref_id}/${props.activity.ref_id}`}
          >
            {bigPlan.name}
            <BigPlanStatusTag status={bigPlan.status} />
            <TimePlanActivityKindTag kind={props.activity.kind} />
            <TimePlanActivityFeasabilityTag
              feasability={props.activity.feasability}
            />
          </EntityLink>
        </EntityCard>
      );
    } else {
      return <></>;
    }
  }