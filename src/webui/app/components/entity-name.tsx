import type { EntityName } from "@jupiter/webapi-client";
import { Typography } from "@mui/material";

interface EntityNameProps {
  compact?: boolean;
  inline?: boolean
  name: EntityName;
}

export function EntityNameComponent({ compact, inline, name }: EntityNameProps) {
  return (
    <Typography sx={{display: inline ? "inline" : "block"}} fontSize={!compact ? "1rem" : "0.85rem"}>{name}</Typography>
  );
}

export function EntityNameOneLineComponent({ compact, name }: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "1rem" : "0.85rem"} noWrap>
      {name}
    </Typography>
  );
}


