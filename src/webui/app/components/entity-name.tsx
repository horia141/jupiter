import { Typography } from "@mui/material";
import type { EntityName } from "jupiter-gen";

interface EntityNameProps {
  compact?: boolean;
  name: EntityName;
}

export function EntityNameComponent({ compact, name }: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "1rem" : "0.85rem"}>
      {name.the_name}
    </Typography>
  );
}

export function EntityNameOneLineComponent({ compact, name }: EntityNameProps) {
  return (
    <Typography fontSize={!compact ? "1rem" : "0.85rem"} noWrap>
      {name.the_name}
    </Typography>
  );
}
