import { WorkspaceFeature } from "@jupiter/webapi-client";
import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Typography,
} from "@mui/material";
import { Link } from "@remix-run/react";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";

interface InboxTasksNoNothingCardProps {
  topLevelInfo: TopLevelInfo;
}

export function InboxTasksNoNothingCard(props: InboxTasksNoNothingCardProps) {
  let initialText = "There are no inbox tasks to show. ";
  const { workspace } = props.topLevelInfo;

  const habitsAvailable = isWorkspaceFeatureAvailable(
    workspace,
    WorkspaceFeature.HABITS
  );
  const choresAvailable = isWorkspaceFeatureAvailable(
    workspace,
    WorkspaceFeature.CHORES
  );

  if (habitsAvailable && choresAvailable) {
    initialText += "You can create a new habit, chore, or inbox task.";
  } else if (habitsAvailable) {
    initialText += "You can create a new habit or inbox task.";
  } else if (choresAvailable) {
    initialText += "You can create a new chore or inbox task.";
  } else {
    initialText += "You can create a new inbox task.";
  }

  return (
    <Card>
      <CardHeader title="No Inbox Tasks" />
      <CardContent>
        <Typography variant="body1">{initialText}</Typography>
      </CardContent>
      <CardActions>
        {isWorkspaceFeatureAvailable(
          props.topLevelInfo.workspace,
          WorkspaceFeature.HABITS
        ) && (
          <Button
            variant="contained"
            size="small"
            component={Link}
            to="/workspace/habits/new"
          >
            New Habit
          </Button>
        )}
        {isWorkspaceFeatureAvailable(
          props.topLevelInfo.workspace,
          WorkspaceFeature.CHORES
        ) && (
          <Button
            variant="contained"
            size="small"
            component={Link}
            to="/workspace/chores/new"
          >
            New Chore
          </Button>
        )}
        <Button
          variant="contained"
          size="small"
          component={Link}
          to="/workspace/inbox-tasks/new"
        >
          New Inbox Task
        </Button>
      </CardActions>
    </Card>
  );
}
