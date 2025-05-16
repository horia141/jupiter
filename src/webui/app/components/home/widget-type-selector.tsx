import { MenuItem, Select, Typography } from "@mui/material";
import {
  HomeTabTarget,
  WidgetType,
  WidgetTypeConstraints,
} from "@jupiter/webapi-client";
import { useEffect, useState } from "react";

import { widgetTypeName } from "~/logic/widget";

interface WidgetTypeSelectorProps {
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
    props.widgetConstraints[type].for_tab_target.includes(props.target),
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
        {allowedTypes.map((type) => (
          <MenuItem key={type} value={type}>
            {widgetTypeName(type)}
          </MenuItem>
        ))}
      </Select>
    </>
  );
}
