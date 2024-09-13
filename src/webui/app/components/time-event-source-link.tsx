import type {
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
} from "@jupiter/webapi-client";
import { TimeEventNamespace } from "@jupiter/webapi-client";
import LaunchIcon from "@mui/icons-material/Launch";
import { Button } from "@mui/material";
import { Link } from "@remix-run/react";

interface TimeEventSourceLinkProps {
  timeEvent: TimeEventFullDaysBlock | TimeEventInDayBlock;
}

export function TimeEventSourceLink(props: TimeEventSourceLinkProps) {
  switch (props.timeEvent.namespace) {
    case TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/workspace/calendar/schedule/full-days/${props.timeEvent.source_entity_ref_id}`}
        >
          Link
        </Button>
      );
    }

    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/workspace/calendar/schedule/in-day/${props.timeEvent.source_entity_ref_id}`}
        >
          Link
        </Button>
      );
    }

    case TimeEventNamespace.PERSON_BIRTHDAY: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/workspace/persons/${props.timeEvent.source_entity_ref_id}`}
        >
          Link
        </Button>
      );
    }

    case TimeEventNamespace.INBOX_TASK: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/workspace/inbox-tasks/${props.timeEvent.source_entity_ref_id}`}
        >
          Link
        </Button>
      );
    }

    case TimeEventNamespace.VACATION: {
      return (
        <Button
          startIcon={<LaunchIcon />}
          variant="outlined"
          size="small"
          component={Link}
          to={`/workspace/vacations/${props.timeEvent.source_entity_ref_id}`}
        >
          Link
        </Button>
      );
    }

    default: {
      throw new Error("Unknown namespace");
    }
  }
}
