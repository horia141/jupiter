import { MenuItem, Select, Typography } from "@mui/material";
import {
  HomeTabTarget,
  User,
  WidgetType,
  WidgetTypeConstraints,
  Workspace,
} from "@jupiter/webapi-client";
import { useEffect, useState } from "react";

import { isAllowedForWidgetConstraints, widgetTypeName } from "~/logic/widget";

interface WidgetTypeSelectorProps {
  user: User;
  workspace: Workspace;
  name: string;
  value?: WidgetType;
  defaultValue?: WidgetType;
  onChange?: (type: WidgetType) => void;
  inputsEnabled: boolean;
  target: HomeTabTarget;
  widgetConstraints: Record<string, WidgetTypeConstraints>;
}

export function WidgetTypeSelector(props: WidgetTypeSelectorProps) {
  const [theType, setTheType] = useState(
    props.value || props.defaultValue || WidgetType.MOTD,
  );
  useEffect(() => {
    setTheType(props.value || props.defaultValue || WidgetType.MOTD);
  }, [props.value, props.defaultValue]);

  const allowedTypes = Object.values(WidgetType).filter((type) =>
    props.widgetConstraints[type].allowed_dimensions[props.target].includes(
      props.widgetConstraints[type].allowed_dimensions[props.target][0],
    ),
  );

  if (allowedTypes.length === 0) {
    return <Typography>No types allowed for this widget type</Typography>;
  }

  return (
    <>
      <Select
        name={props.name}
        value={theType}
        disabled={!props.inputsEnabled}
        fullWidth
        onChange={(event) => {
          setTheType(event.target.value as WidgetType);
          props.onChange?.(event.target.value as WidgetType);
        }}
      >
        {allowedTypes.map((type) => {
          const constraints = props.widgetConstraints[type];

          return (
            <MenuItem
              key={type}
              value={type}
              disabled={
                !isAllowedForWidgetConstraints(
                  constraints,
                  props.user,
                  props.workspace,
                )
              }
            >
              {widgetTypeName(type)}
            </MenuItem>
          );
        })}
      </Select>
    </>
  );
}
