import { Box, Chip, MenuItem, Select } from "@mui/material";
import { NamedEntityTag } from "jupiter-gen";
import { entityTagName } from "~/logic/domain/entity-tag";
import { inferEntityTagsForEnabledFeatures } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";

interface EntityTagSelectProps {
  topLevelInfo: TopLevelInfo;
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
  defaultValue?: Array<NamedEntityTag>;
  value?: Array<NamedEntityTag>;
  onChange?: (e: Array<NamedEntityTag>) => void;
}

export function EntityTagSelect(props: EntityTagSelectProps) {
  const allowedEntityTags = inferEntityTagsForEnabledFeatures(
    props.topLevelInfo.workspace,
    Object.values(NamedEntityTag)
  );

  return (
    <Select
      labelId={props.labelId}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      multiple
      defaultValue={props.defaultValue}
      value={props.value}
      onChange={(e) => {
        if (props.onChange === undefined) {
          return;
        }

        props.onChange(e.target.value as Array<NamedEntityTag>);
      }}
      renderValue={(selected) => (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
          {selected.map((value) => (
            <Chip key={value} label={entityTagName(value)} />
          ))}
        </Box>
      )}
      label={props.label}
    >
      {allowedEntityTags.map((st) => (
        <MenuItem key={st} value={st}>
          {entityTagName(st)}
        </MenuItem>
      ))}
    </Select>
  );
}
