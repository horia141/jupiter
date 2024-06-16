import { WorkspaceFeature } from "@jupiter/webapi-client";
import { Button, ButtonGroup } from "@mui/material";
import { Link } from "@remix-run/react";
import React, { useState } from "react";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { TopLevelInfo } from "~/top-level-context";

interface NavSingleDesc {
  kind: "nav-single";
  text: string;
  link: string;
  icon?: JSX.Element;
  gatedOn?: WorkspaceFeature;
}

interface NavMultipleDesc {
  kind: "nav-multiple";
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

export function NavMultiple(...navs: Array<NavSingleDesc>): NavMultipleDesc {
  return {
    kind: "nav-multiple",
    navs: navs,
  };
}

interface SectionActionsProps {
  id: string;
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  actions: Array<ActionDesc>;
}

export function SectionActions(props: SectionActionsProps) {
  return (
    <>
      {props.actions.map((action, index) => (
        <ActionView
          key={`action-${props.id}-${index}`}
          topLevelInfo={props.topLevelInfo}
          inputsEnabled={props.inputsEnabled}
          action={action}
        />
      ))}
    </>
  );
}

interface ActionViewProps {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
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
          action={props.action}
        />
      );

    case "filter-few-options":
        return (
            <FilterFewOptionsView
                topLevelInfo={props.topLevelInfo}
                inputsEnabled={props.inputsEnabled}
                action={props.action} />
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
  action: NavMultipleDesc;
}

function NavMultipleView(props: NavMultipleViewProps) {
  return (
    <ButtonGroup>
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

interface FilterFewOptionsViewProps<K> {
    topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  action: FilterFewOptionsDesc<K>;
}

function FilterFewOptionsView<K>(props: FilterFewOptionsViewProps<K>) {
    const [selected, setSelected] = useState<K>(props.action.defaultOption);

    return (
        <ButtonGroup>
          {props.action.options.map((option, index) => {
            if (option.gatedOn) {
              const workspace = props.topLevelInfo.workspace;
              if (!isWorkspaceFeatureAvailable(workspace, option.gatedOn)) {
                return (
                  <React.Fragment key={`filter-few-options-${index}`}></React.Fragment>
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