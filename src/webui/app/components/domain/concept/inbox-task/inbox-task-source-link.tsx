import type { InboxTaskLoadResult } from "@jupiter/webapi-client";
import { InboxTaskSource } from "@jupiter/webapi-client";
import LaunchIcon from "@mui/icons-material/Launch";
import { Button } from "@mui/material";
import { Link } from "@remix-run/react";

import { useBigScreen } from "~/rendering/use-big-screen";

interface InboxTaskSourceLinkProps {
  inboxTaskResult: InboxTaskLoadResult;
}

export function InboxTaskSourceLink(props: InboxTaskSourceLinkProps) {
  const isBigScreen = useBigScreen();

  switch (props.inboxTaskResult.inbox_task.source) {
    case InboxTaskSource.WORKING_MEM_CLEANUP: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/working-mem/archive/${props.inboxTaskResult.working_mem?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Working Mem" : "WM"}
        </Button>
      );
    }

    case InboxTaskSource.TIME_PLAN: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/time-plans/${props.inboxTaskResult.time_plan?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Time Plan" : "TP"}
        </Button>
      );
    }

    case InboxTaskSource.HABIT: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/habits/${props.inboxTaskResult.habit?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Habit" : "H"}
        </Button>
      );
    }

    case InboxTaskSource.CHORE: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/chores/${props.inboxTaskResult.chore?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Chore" : "C"}
        </Button>
      );
    }

    case InboxTaskSource.BIG_PLAN: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/big-plans/${props.inboxTaskResult.big_plan?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Big Plan" : "BP"}
        </Button>
      );
    }

    case InboxTaskSource.JOURNAL: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/journals/${props.inboxTaskResult.journal?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Journal" : "J"}
        </Button>
      );
    }

    case InboxTaskSource.METRIC: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/metrics/${props.inboxTaskResult.metric?.ref_id}/details`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Metric" : "M"}
        </Button>
      );
    }

    case InboxTaskSource.PERSON_CATCH_UP: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/persons/${props.inboxTaskResult.person?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Person" : "P"}
        </Button>
      );
    }

    case InboxTaskSource.PERSON_BIRTHDAY: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/persons/${props.inboxTaskResult.person?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Person" : "P"}
        </Button>
      );
    }

    case InboxTaskSource.SLACK_TASK: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/push-integration/slack-tasks/${props.inboxTaskResult.slack_task?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Slack Task" : "ST"}
        </Button>
      );
    }

    case InboxTaskSource.EMAIL_TASK: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/app/workspace/push-integration/email-tasks/${props.inboxTaskResult.email_task?.ref_id}`}
          sx={{ flexGrow: 1 }}
        >
          {isBigScreen ? "Email Task" : "ET"}
        </Button>
      );
    }

    default: {
      return null;
    }
  }
}
