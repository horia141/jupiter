import type { EntityName } from "@jupiter/webapi-client";
import { Typography } from "@mui/material";

interface EntityNameProps {
  compact?: boolean;
  name: EntityName;
}

export function EntityNameComponent({ compact, name }: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "unset" : "0.85rem"}>{name}</Typography>
  );
}

export function EntityNameOneLineComponent({ compact, name }: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "unset" : "0.85rem"} noWrap>
      {name}
    </Typography>
  );
}
