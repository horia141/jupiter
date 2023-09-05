import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Typography,
} from "@mui/material";
import { Link } from "@remix-run/react";

interface NoTasksCardProps {
  parent: string;
  parentNewLocations: string;
}

export function NoTasksCard(props: NoTasksCardProps) {
  return (
    <Card>
      <CardHeader title="No Inbox Tasks" />
      <CardContent>
        <Typography variant="body1">
          There are no inbox tasks to show. You can generate some new tasks, or
          create a new {props.parent}.
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          variant="contained"
          size="small"
          component={Link}
          to="/workspace/tools/gen"
          preventScrollReset
        >
          Generate
        </Button>
        <Button
          variant="contained"
          size="small"
          component={Link}
          preventScrollReset
          to={props.parentNewLocations}
        >
          Create
        </Button>
      </CardActions>
    </Card>
  );
}
