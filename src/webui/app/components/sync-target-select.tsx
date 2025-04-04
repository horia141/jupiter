import { SyncTarget } from "@jupiter/webapi-client";
import { Box, Chip, MenuItem, Select } from "@mui/material";

import { syncTargetName } from "~/logic/domain/sync-target";
import { inferSyncTargetsForEnabledFeatures } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";

interface SyncTargetSelectProps {
  topLevelInfo: TopLevelInfo;
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
}

export function SyncTargetSelect(props: SyncTargetSelectProps) {
  const allowedSyncTargets = inferSyncTargetsForEnabledFeatures(
    props.topLevelInfo.workspace,
    Object.values(SyncTarget),
  );

  return (
    <Select
      labelId={props.labelId}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      multiple
      defaultValue={[]}
      renderValue={(selected) => (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
          {selected.map((value) => (
            <Chip key={value} label={syncTargetName(value)} />
          ))}
        </Box>
      )}
      label={props.label}
    >
      {allowedSyncTargets.map((st) => (
        <MenuItem key={st} value={st}>
          {syncTargetName(st)}
        </MenuItem>
      ))}
    </Select>
  );
}
