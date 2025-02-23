import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Typography,
} from "@mui/material";
import { Link } from "@remix-run/react";
import type { DocsHelpSubject } from "./docs-help";
import { DocsHelp } from "./docs-help";

interface EntityNoNothingCardProps {
  title: string;
  message: string;
  newEntityLocations: string;
  helpSubject: DocsHelpSubject;
}

export function EntityNoNothingCard(props: EntityNoNothingCardProps) {
  return (
    <Card>
      <CardHeader title={props.title} />
      <CardContent>
        <Typography variant="body1">{props.message}</Typography>

        <Typography variant="body1">
          Or you can learn more in our docs
          <DocsHelp subject={props.helpSubject} size="small" />
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          variant="contained"
          size="small"
          component={Link}
          to={props.newEntityLocations}
        >
          Add New
        </Button>
      </CardActions>
    </Card>
  );
}
