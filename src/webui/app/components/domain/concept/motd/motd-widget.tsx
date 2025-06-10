import { Typography } from "@mui/material";

import { WidgetProps } from "~/components/domain/application/home/common";
import { StandardLink } from "~/components/infra/standard-link";

export function MOTDWidget(props: WidgetProps) {
  const motd = props.motd!;

  return (
    <Typography variant="h6" component="div" sx={{ fontStyle: "italic" }}>
      {motd.quote} -{" "}
      <StandardLink
        inline={"true"}
        to={motd.wikiquote_link}
        target="_blank"
        rel="noopener noreferrer"
      >
        {motd.author}
      </StandardLink>
    </Typography>
  );
}
