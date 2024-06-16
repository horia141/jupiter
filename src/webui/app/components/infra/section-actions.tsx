import type { WorkspaceFeature } from "@jupiter/webapi-client";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import BoltIcon from "@mui/icons-material/Bolt";
import {
  Button,
  ButtonGroup,
  ClickAwayListener,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grow,
  MenuItem,
  MenuList,
  Paper,
  Popper,
  Stack,
} from "@mui/material";
import { Link } from "@remix-run/react";
import React, { useState } from "react";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { useBigScreen } from "~/rendering/use-big-screen";
import type { TopLevelInfo } from "~/top-level-context";

interface NavSingleDesc {
  kind: "nav-single";
  text: string;
  link: string;
  icon?: JSX.Element;
  gatedOn?: WorkspaceFeature;
}

interface NavMultipleDesc {
  kind: "nav-multiple";
  approach: "spread" | "compact";
  navs: Array<NavSingleDesc>;
}

interface FilterOption<K> {
  value: K;
  text: string;
  icon?: JSX.Element;
  gatedOn?: WorkspaceFeature;
}

interface FilterFewOptionsDesc<K> {
  kind: "filter-few-options";
  defaultOption: K;
  options: Array<FilterOption<K>>;
  onSelect: (selected: K) => void;
  hideIfOneOption?: boolean;
}

type ActionDesc =
  | NavSingleDesc // A single button, can be a navigation or a callback
  | NavMultipleDesc // A group of buttons, can be a navigation or a callback
  | FilterFewOptionsDesc<any>; // A group to filter on, can be a navigation or a callback

export function NavSingle(
  text: string,
  link: string,
  icon?: JSX.Element,
  gatedOn?: WorkspaceFeature
): NavSingleDesc {
  return {
    kind: "nav-single",
    text,
    link,
    icon,
    gatedOn,
  };
}

export function NavMultipleSpread(
  ...navs: Array<NavSingleDesc>
): NavMultipleDesc {
  return {
    kind: "nav-multiple",
    approach: "spread",
    navs: navs,
  };
}

export function NavMultipleCompact(
  ...navs: Array<NavSingleDesc>
): NavMultipleDesc {
  return {
    kind: "nav-multiple",
    approach: "compact",
    navs: navs,
  };
}

export function FilterFewOptions<K>(
  options: Array<FilterOption<K>>,
  onSelect: (selected: K) => void
): FilterFewOptionsDesc<K> {
  return {
    kind: "filter-few-options",
    defaultOption: options[0].value,
    options: options,
    onSelect: onSelect,
    hideIfOneOption: true,
  };
}

interface SectionActionsProps {
  id: string;
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  actions: Array<ActionDesc>;
}

export function SectionActions(props: SectionActionsProps) {
  const isBigScreen = useBigScreen();

  const [showExtraActionsDialog, setShowExtraActionsDialog] = useState(false);

  if (!isBigScreen) {
    return (
      <>
        <Button
          disabled={!props.inputsEnabled}
          variant="outlined"
          size="medium"
          color="primary"
          onClick={() => setShowExtraActionsDialog(true)}
        >
          <BoltIcon />
        </Button>

        <Dialog
          onClose={() => setShowExtraActionsDialog(false)}
          open={showExtraActionsDialog}
        >
          <DialogTitle>Actions</DialogTitle>
          <DialogContent>
            <Stack spacing={2}>
              {props.actions.map((action, index) => (
                <ActionView
                  key={`action-${props.id}-${index}`}
                  topLevelInfo={props.topLevelInfo}
                  inputsEnabled={props.inputsEnabled}
                  orientation="vertical"
                  action={action}
                />
              ))}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowExtraActionsDialog(false)}>
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </>
    );
  }

  return (
    <Stack direction="row" spacing={1} sx={{ padding: "0.25rem" }}>
      {props.actions.map((action, index) => (
        <ActionView
          key={`action-${props.id}-${index}`}
          topLevelInfo={props.topLevelInfo}
          inputsEnabled={props.inputsEnabled}
          orientation="horizontal"
          action={action}
        />
      ))}
    </Stack>
  );
}

interface ActionViewProps {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  orientation: "horizontal" | "vertical";
  action: ActionDesc;
}

function ActionView(props: ActionViewProps) {
  switch (props.action.kind) {
    case "nav-single":
      return (
        <NavSingleView
          topLevelInfo={props.topLevelInfo}
          inputsEnabled={props.inputsEnabled}
          action={props.action}
        />
      );

    case "nav-multiple":
      return (
        <NavMultipleView
          topLevelInfo={props.topLevelInfo}
          inputsEnabled={props.inputsEnabled}
          orientation={props.orientation}
          action={props.action}
        />
      );

    case "filter-few-options":
      return (
        <FilterFewOptionsView
          topLevelInfo={props.topLevelInfo}
          inputsEnabled={props.inputsEnabled}
          orientation={props.orientation}
          action={props.action}
        />
      );
  }
}

interface NavSingleViewProps {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  action: NavSingleDesc;
}

function NavSingleView(props: NavSingleViewProps) {
  if (props.action.gatedOn) {
    const workspace = props.topLevelInfo.workspace;
    if (!isWorkspaceFeatureAvailable(workspace, props.action.gatedOn)) {
      return <></>;
    }
  }

  return (
    <Button
      variant="outlined"
      component={Link}
      disabled={!props.inputsEnabled}
      startIcon={props.action.icon}
      to={props.action.link}
    >
      {props.action.text}
    </Button>
  );
}

interface NavMultipleViewProps {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  orientation: "horizontal" | "vertical";
  action: NavMultipleDesc;
}

function NavMultipleView(props: NavMultipleViewProps) {
  switch (props.action.approach) {
    case "spread":
      return <NavMultipleSpreadView {...props} />;
    case "compact":
      return <NavMultipleCompactView {...props} />;
  }
}

function NavMultipleSpreadView(props: NavMultipleViewProps) {
  return (
    <ButtonGroup orientation={props.orientation}>
      {props.action.navs.map((nav, index) => {
        if (nav.gatedOn) {
          const workspace = props.topLevelInfo.workspace;
          if (!isWorkspaceFeatureAvailable(workspace, nav.gatedOn)) {
            return (
              <React.Fragment key={`nav-multiple-${index}`}></React.Fragment>
            );
          }
        }

        return (
          <Button
            key={`nav-multiple-${index}`}
            variant="outlined"
            component={Link}
            disabled={!props.inputsEnabled}
            startIcon={nav.icon}
            to={nav.link}
          >
            {nav.text}
          </Button>
        );
      })}
    </ButtonGroup>
  );
}

function NavMultipleCompactView(props: NavMultipleViewProps) {
  const [open, setOpen] = useState(false);
  const anchorRef = React.useRef<HTMLDivElement>(null);
  const [selectedIndex, setSelectedIndex] = React.useState(1);

  const realActions: NavSingleDesc[] = [];
  for (const action of props.action.navs) {
    if (action.gatedOn) {
      const workspace = props.topLevelInfo.workspace;
      if (!isWorkspaceFeatureAvailable(workspace, action.gatedOn)) {
        continue;
      }
    }
    realActions.push(action);
  }

  function handleMenuItemClick(
    event: React.MouseEvent<HTMLElement, MouseEvent>,
    index: number
  ) {
    setSelectedIndex(index);
    setOpen(false);
  }

  function handleClose(event: Event) {
    if (
      anchorRef.current &&
      anchorRef.current.contains(event.target as HTMLElement)
    ) {
      return;
    }

    setOpen(false);
  }

  if (realActions.length === 0) {
    return <></>;
  }

  return (
    <>
      <ButtonGroup ref={anchorRef}>
        <Button
          disabled={!props.inputsEnabled}
          component={Link}
          startIcon={realActions[selectedIndex].icon}
          to={realActions[selectedIndex].link}
        >
          {realActions[selectedIndex].text}
        </Button>
        <Button
          size="small"
          disabled={!props.inputsEnabled}
          onClick={() => setOpen((prevOpen) => !prevOpen)}
        >
          <ArrowDropDownIcon />
        </Button>
      </ButtonGroup>
      <Popper
        sx={{
          zIndex: 20000,
        }}
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
      >
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{
              transformOrigin:
                placement === "bottom" ? "center top" : "center bottom",
            }}
          >
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList id="split-button-menu" autoFocusItem>
                  {realActions.map((option, index) => (
                    <MenuItem
                      key={`nav-multiple-${index}`}
                      selected={index === selectedIndex}
                      onClick={(event) => handleMenuItemClick(event, index)}
                    >
                      {option.text}
                    </MenuItem>
                  ))}
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
}

interface FilterFewOptionsViewProps<K> {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  orientation: "horizontal" | "vertical";
  action: FilterFewOptionsDesc<K>;
}

function FilterFewOptionsView<K>(props: FilterFewOptionsViewProps<K>) {
  const [selected, setSelected] = useState<K>(props.action.defaultOption);

  return (
    <ButtonGroup orientation={props.orientation}>
      {props.action.options.map((option, index) => {
        if (option.gatedOn) {
          const workspace = props.topLevelInfo.workspace;
          if (!isWorkspaceFeatureAvailable(workspace, option.gatedOn)) {
            return (
              <React.Fragment
                key={`filter-few-options-${index}`}
              ></React.Fragment>
            );
          }
        }

        return (
          <Button
            key={`filter-few-options-${index}`}
            variant={option.value === selected ? "contained" : "outlined"}
            disabled={!props.inputsEnabled}
            startIcon={option.icon}
            onClick={() => {
              setSelected(option.value);
              props.action.onSelect(option.value);
            }}
          >
            {option.text}
          </Button>
        );
      })}
    </ButtonGroup>
  );
}
