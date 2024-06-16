import type { WorkspaceFeature } from "@jupiter/webapi-client";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import BoltIcon from "@mui/icons-material/Bolt";
import CheckBoxIcon from "@mui/icons-material/CheckBox";
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import {
  Autocomplete,
  Button,
  ButtonGroup,
  Checkbox,
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
  TextField,
  useTheme,
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

interface FilterManyOptionsDesc<K> {
  kind: "filter-many-options";
  title: string;
  options: Array<FilterOption<K>>;
  onSelect: (selected: Array<K>) => void;
  hideIfOneOption?: boolean;
}

type ActionDesc =
  | NavSingleDesc // A single button, can be a navigation or a callback
  | NavMultipleDesc // A group of buttons, can be a navigation or a callback
  | FilterFewOptionsDesc<any> // A group to filter on, can be a navigation or a callback
  | FilterManyOptionsDesc<any>; // A group to filter on, with many options

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

export function FilterManyOptions<K>(
  title: string,
  options: Array<FilterOption<K>>,
  onSelect: (selected: Array<K>) => void
): FilterManyOptionsDesc<K> {
  return {
    kind: "filter-many-options",
    title: title,
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
  extraActions?: Array<ActionDesc>;
}

export function SectionActions(props: SectionActionsProps) {
  const isBigScreen = useBigScreen();

  if (!isBigScreen) {
    const allActions = props.actions.concat(props.extraActions ?? []);
    return (
      <SectionActionsWithDialog
        id={props.id}
        topLevelInfo={props.topLevelInfo}
        inputsEnabled={props.inputsEnabled}
        actions={allActions}
      />
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

      <SectionActionsWithDialog
        id={props.id}
        topLevelInfo={props.topLevelInfo}
        inputsEnabled={props.inputsEnabled}
        actions={props.extraActions ?? []}
      />
    </Stack>
  );
}

interface SectionActionsWithDialogProps {
  id: string;
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  actions: Array<ActionDesc>;
}

function SectionActionsWithDialog(props: SectionActionsWithDialogProps) {
  const [showExtraActionsDialog, setShowExtraActionsDialog] = useState(false);

  if (props.actions.length === 0) {
    return <></>;
  }

  return (
    <>
      <Button
        disabled={!props.inputsEnabled}
        variant="outlined"
        size="medium"
        color="primary"
        sx={{ margin: "0.25rem" }}
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

    case "filter-many-options":
      return (
        <FilterManyOptionsView
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
  const theme = useTheme();
  const isBigScreen = useBigScreen();

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
          zIndex: theme.zIndex.appBar + 20,
          backgroundColor: theme.palette.background.paper,
        }}
        open={open}
        anchorEl={anchorRef.current}
        disablePortal={!isBigScreen}
        transition
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

  const realOptions: FilterOption<K>[] = [];
  for (const option of props.action.options) {
    if (option.gatedOn) {
      const workspace = props.topLevelInfo.workspace;
      if (!isWorkspaceFeatureAvailable(workspace, option.gatedOn)) {
        continue;
      }
    }
    realOptions.push(option);
  }

  if (realOptions.length === 0) {
    return <></>;
  }

  if (props.action.hideIfOneOption && realOptions.length === 1) {
    return <></>;
  }

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

interface FilterManyOptionsViewProps<K> {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  orientation: "horizontal" | "vertical";
  action: FilterManyOptionsDesc<K>;
}

function FilterManyOptionsView<K>(props: FilterManyOptionsViewProps<K>) {
  const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
  const checkedIcon = <CheckBoxIcon fontSize="small" />;

  const [selected, setSelected] = useState<FilterOption<K>[]>([]);

  const realOptions: FilterOption<K>[] = [];
  for (const option of props.action.options) {
    if (option.gatedOn) {
      const workspace = props.topLevelInfo.workspace;
      if (!isWorkspaceFeatureAvailable(workspace, option.gatedOn)) {
        continue;
      }
    }
    realOptions.push(option);
  }

  if (realOptions.length === 0) {
    return <></>;
  }

  if (props.action.hideIfOneOption && realOptions.length === 1) {
    return <></>;
  }

  return (
    <Autocomplete
      multiple
      disableCloseOnSelect
      size="small"
      options={realOptions}
      limitTags={2}
      getOptionLabel={(option) => option.text}
      value={selected}
      onChange={(_, selected) => {
        setSelected(selected);
        props.action.onSelect(selected.map((option) => option.value));
      }}
      isOptionEqualToValue={(option, value) => option.value === value.value}
      renderOption={(props, option, { selected }) => (
        <li {...props}>
          <Checkbox
            icon={icon}
            checkedIcon={checkedIcon}
            style={{ marginRight: 8 }}
            checked={selected}
          />
          {option.text}
        </li>
      )}
      style={{ minWidth: "180px" }}
      renderInput={(params) => (
        <TextField
          {...params}
          multiline={false}
          label={props.action.title}
          placeholder={props.action.title}
        />
      )}
    />
  );
}
