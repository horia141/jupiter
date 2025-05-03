import { Card, CardContent, Typography } from "@mui/material";
import type { MOTD } from "@jupiter/webapi-client";

interface MOTDWidgetProps {
  motd: MOTD;
}

export function MOTDWidget(props: MOTDWidgetProps) {
  return (
    <Card sx={{ marginBottom: 2 }}>
      <CardContent>
        <Typography variant="h6" component="div" sx={{ fontStyle: "italic" }}>
          {props.motd.quote} -{" "}
          <a
            href={props.motd.wikiquote_link}
            target="_blank"
            rel="noopener noreferrer"
          >
            {props.motd.author}
          </a>
        </Typography>
      </CardContent>
    </Card>
  );
}
