import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Typography,
} from "@mui/material";
import { Link } from "@remix-run/react";

export function NoNothingCard() {
  return (
    <Card>
      <CardHeader title="No Inbox Tasks" />
      <CardContent>
        <Typography variant="body1">
          There are no inbox tasks to show. You can create a new habit, chore,
          or inbox task.
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          variant="contained"
          size="small"
          component={Link}
          to="/workspace/habits/new"
        >
          New Habit
        </Button>
        <Button
          variant="contained"
          size="small"
          component={Link}
          to="/workspace/chores/new"
        >
          New Chore
        </Button>
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
