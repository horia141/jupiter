import {
  HomeTab,
  HomeTabTarget,
  HomeWidget,
  SmallScreenHomeTabWidgetPlacement,
  WidgetGeometry,
} from "@jupiter/webapi-client";
import {
  Button,
  DialogTitle,
  Dialog,
  DialogContent,
  DialogActions,
  Stack,
  Box,
} from "@mui/material";
import { useState } from "react";

import { isWidgetDimensionKSized, widgetDimensionRows } from "~/logic/widget";

interface WidgetPlacementQuickSelectorProps {
  target: HomeTabTarget;
  homeTab: HomeTab;
  widgets: HomeWidget[];
  onRowAndColChange: (row: number, col: number) => void;
  hightlightGeometry?: WidgetGeometry;
}

export function WidgetPlacementQuickSelector(
  props: WidgetPlacementQuickSelectorProps,
) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button variant="contained" color="primary" onClick={() => setOpen(true)}>
        Pick
      </Button>
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Pick a widget placement</DialogTitle>
        <DialogContent>
          <TheWidgetPlacement
            target={props.target}
            homeTab={props.homeTab}
            widgets={props.widgets}
            onRowAndColChange={(row, col) => {
              props.onRowAndColChange(row, col);
              setOpen(false);
            }}
            hightlightGeometry={props.hightlightGeometry}
          />
        </DialogContent>
        <DialogActions>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setOpen(false)}
          >
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

function TheWidgetPlacement(props: WidgetPlacementQuickSelectorProps) {
  switch (props.target) {
    case HomeTabTarget.BIG_SCREEN:
      return <BigScreenWidgetPlacement {...props} />;
    case HomeTabTarget.SMALL_SCREEN:
      return <SmallScreenWidgetPlacement {...props} />;
  }
}

function BigScreenWidgetPlacement(props: WidgetPlacementQuickSelectorProps) {
  return <>Here</>;
}

function SmallScreenWidgetPlacement(props: WidgetPlacementQuickSelectorProps) {
  const widgetPlacement = props.homeTab
    .widget_placement as SmallScreenHomeTabWidgetPlacement;
  const widgetByRefId = new Map(props.widgets.map((w) => [w.ref_id, w]));

  return (
    <Stack useFlexGap direction="column" sx={{ alignItems: "center" }}>
      {widgetPlacement.matrix.map((row, rowIndex) => {
        if (row === null) {
          // Check if there's a k-sized widget before this row
          for (let i = 0; i < rowIndex; i++) {
            const prevWidgetId = widgetPlacement.matrix[i];
            if (prevWidgetId !== null) {
              const prevWidget = widgetByRefId.get(prevWidgetId);
              if (
                prevWidget &&
                isWidgetDimensionKSized(prevWidget.geometry.dimension)
              ) {
                return null;
              }
            }
          }

          return (
            <MoveWidgetButton
              key={rowIndex}
              row={rowIndex}
              col={0}
              onClick={() => props.onRowAndColChange(rowIndex, 0)}
              highlightGeometry={props.hightlightGeometry}
            />
          );
        }

        // If the previous widget is the same as the current one, don't render the current block,
        // since this is a bigger widget that is taking up the space of the smaller one.
        if (
          rowIndex > 0 &&
          widgetPlacement.matrix[rowIndex] ===
            widgetPlacement.matrix[rowIndex - 1]
        ) {
          return null;
        }

        const widget = widgetByRefId.get(row)!;

        return (
          <PlacedWidget
            key={rowIndex}
            widget={widget}
            row={rowIndex}
            col={0}
            highlightGeometry={props.hightlightGeometry}
          />
        );
      })}
    </Stack>
  );
}

interface MoveWidgetButtonProps {
  row: number;
  col: number;
  onClick: () => void;
  highlightGeometry?: WidgetGeometry;
}

function MoveWidgetButton(props: MoveWidgetButtonProps) {
  const shouldHighlight =
    props.highlightGeometry &&
    props.highlightGeometry.row === props.row &&
    props.highlightGeometry.col === props.col;

  return (
    <Button
      variant="outlined"
      color="primary"
      onClick={props.onClick}
      sx={{
        width: "8rem",
        height: "3rem",
        color: (theme) =>
          shouldHighlight
            ? theme.palette.primary.contrastText
            : theme.palette.primary.main,
        backgroundColor: (theme) =>
          shouldHighlight ? theme.palette.primary.light : "transparent",
      }}
    >
      Move
    </Button>
  );
}

interface PlacedWidgetProps {
  widget: HomeWidget;
  row: number;
  col: number;
  highlightGeometry?: WidgetGeometry;
}

function PlacedWidget(props: PlacedWidgetProps) {
  const heightInRem = widgetDimensionRows(props.widget.geometry.dimension) * 3;
  const shouldHighlight =
    props.highlightGeometry &&
    props.highlightGeometry.row === props.row &&
    props.highlightGeometry.col === props.col;

  return (
    <Box
      sx={{
        fontSize: "0.64rem",
        width: "8rem",
        height: `${heightInRem}rem`,
        border: (theme) => `2px dotted ${theme.palette.primary.main}`,
        borderRadius: "4px",
        borderBottomLeftRadius: isWidgetDimensionKSized(
          props.widget.geometry.dimension,
        )
          ? 0
          : "4px",
        borderBottomRightRadius: isWidgetDimensionKSized(
          props.widget.geometry.dimension,
        )
          ? 0
          : "4px",
        borderBottom: (theme) =>
          isWidgetDimensionKSized(props.widget.geometry.dimension)
            ? `4px dotted ${theme.palette.primary.main}`
            : `2px dotted ${theme.palette.primary.main}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: (theme) =>
          shouldHighlight
            ? theme.palette.primary.contrastText
            : theme.palette.primary.main,
        backgroundColor: (theme) =>
          shouldHighlight ? theme.palette.primary.light : "transparent",
      }}
    >
      {props.widget.name}
    </Box>
  );
}
