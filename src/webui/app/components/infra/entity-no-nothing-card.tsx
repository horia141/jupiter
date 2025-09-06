import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Typography,
} from "@mui/material";
import { Form, Link } from "@remix-run/react";

import type { DocsHelpSubject } from "~/components/infra/docs-help";
import { DocsHelp } from "~/components/infra/docs-help";

interface EntityNoNothingCardProps {
  title: string;
  message: string;
  newEntityLocations?: string;
  newEntityAction?: string;
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
        {props.newEntityLocations && (
          <Button
            variant="contained"
            size="small"
            component={Link}
            to={props.newEntityLocations}
          >
            Add New
          </Button>
        )}
        {props.newEntityAction && (
          <Form method="post">
            <Button
              variant="contained"
              size="small"
              type="submit"
              name="intent"
              value={props.newEntityAction}
            >
              Add New
            </Button>
          </Form>
        )}
      </CardActions>
    </Card>
  );
}
