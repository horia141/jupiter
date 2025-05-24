import { MenuItem, Select, Typography } from "@mui/material";
import {
  HomeTabTarget,
  WidgetDimension,
  WidgetType,
  WidgetTypeConstraints,
} from "@jupiter/webapi-client";
import { useEffect, useState } from "react";

import { widgetDimensionName } from "~/logic/widget";

interface WidgetDimensionSelectorProps {
  name: string;
  value?: WidgetDimension;
  defaultValue?: WidgetDimension;
  onChange?: (dimension: WidgetDimension) => void;
  inputsEnabled?: boolean;
  target: HomeTabTarget;
  widgetType: WidgetType;
  widgetConstraints: Record<string, WidgetTypeConstraints>;
}

export function WidgetDimensionSelector(props: WidgetDimensionSelectorProps) {
  const [theDimension, setTheDimension] = useState(
    props.value ||
      props.defaultValue ||
      props.widgetConstraints[props.widgetType].allowed_dimensions[0],
  );
  const constraintForType = props.widgetConstraints[props.widgetType];

  useEffect(() => {
    setTheDimension(
      props.value ||
        props.defaultValue ||
        props.widgetConstraints[props.widgetType].allowed_dimensions[0],
    );
  }, [
    props.value,
    props.defaultValue,
    props.widgetConstraints,
    props.widgetType,
  ]);

  if (!constraintForType) {
    return <Typography>No constraints for this widget type</Typography>;
  }

  if (Object.keys(constraintForType.allowed_dimensions).length === 0) {
    return <Typography>No dimensions allowed for this widget type</Typography>;
  }

  const constraintForTarget =
    constraintForType.allowed_dimensions[props.target];

  if (!constraintForTarget) {
    return <Typography>No dimensions allowed for this widget type</Typography>;
  }

  return (
    <>
      <Select
        name={props.name}
        value={theDimension}
        disabled={!props.inputsEnabled}
        fullWidth
        onChange={(event) => {
          setTheDimension(event.target.value as WidgetDimension);
          props.onChange?.(event.target.value as WidgetDimension);
        }}
      >
        {constraintForTarget.map((dimension) => (
          <MenuItem key={dimension} value={dimension}>
            {widgetDimensionName(dimension as WidgetDimension)}
          </MenuItem>
        ))}
      </Select>
    </>
  );
}
