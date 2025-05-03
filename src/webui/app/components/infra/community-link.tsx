import { IconButton } from "@mui/material";
import { useContext } from "react";

import { GlobalPropertiesContext } from "~/global-properties-client";
import { default as DiscordIcon } from "~/components/infra/discord-icon";

export function CommunityLink() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <IconButton
      component={"a"}
      size={"medium"}
      disableRipple
      color="inherit"
      href={globalProperties.communityUrl}
      target="_blank"
    >
      <DiscordIcon
        style={{ verticalAlign: "middle", width: "1.5rem", height: "1.5rem" }}
      />
    </IconButton>
  );
}
