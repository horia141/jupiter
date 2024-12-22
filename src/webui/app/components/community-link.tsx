import { Box } from "@mui/material";
import { Link } from "@remix-run/react";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { default as DiscordIcon } from "./discord-icon";

interface CommunityLinkProps {}

export function CommunityLink(props: CommunityLinkProps) {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <Box sx={{ width: "1.5rem", height: "1.5rem" }}>
      <Link to={globalProperties.communityUrl} target="_blank" rel="noreferrer">
        <DiscordIcon style={{ verticalAlign: "middle" }} />
      </Link>
    </Box>
  );
}
