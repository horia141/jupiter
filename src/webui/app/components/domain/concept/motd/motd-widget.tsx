import { Typography } from "@mui/material";

import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";

export function MOTDWidget(props: WidgetProps) {
  const motd = props.motd!;

  return (
    <WidgetContainer>
      <Typography variant="h6" component="div" sx={{ fontStyle: "italic" }}>
        {motd.quote} -{" "}
        <a href={motd.wikiquote_link} target="_blank" rel="noopener noreferrer">
          {motd.author}
        </a>
      </Typography>
    </WidgetContainer>
  );
}
