import type { EntityName } from "@jupiter/webapi-client";
import type { SxProps, Theme } from "@mui/material";
import { Typography } from "@mui/material";

interface EntityNameProps {
  compact?: boolean;
  name: EntityName;
  color?: string;
  sx?: SxProps<Theme>;
}

export function EntityNameComponent({
  compact,
  name,
  color,
  sx,
}: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "unset" : "0.85rem"} color={color} sx={sx}>
      {name}
    </Typography>
  );
}

export function EntityNameOneLineComponent({ compact, name }: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "unset" : "0.85rem"} noWrap>
      {name}
    </Typography>
  );
}
