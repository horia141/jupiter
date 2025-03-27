import type {
  Hosting,
  UserFeatureFlagsControls,
  WorkspaceFeatureFlagsControls,
} from "@jupiter/webapi-client";
import {
  FeatureControl,
  UserFeature,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import { FormControl, FormControlLabel, Switch, Tooltip } from "@mui/material";
import {
  featureControlImpliesReadonly,
  userFeatureName,
  userFeatureToDocsHelpSubject,
  workspaceFeatureName,
  workspaceFeatureToDocsHelpSubject,
} from "~/logic/domain/feature";
import { hostingName } from "~/logic/domain/hosting";
import { DocsHelp } from "./docs-help";

interface UserFeatureFlagsEditorProps {
  name: string;
  inputsEnabled: boolean;
  featureFlagsControls: UserFeatureFlagsControls;
  defaultFeatureFlags: Record<string, boolean>;
  hosting: Hosting;
}

export function UserFeatureFlagsEditor(props: UserFeatureFlagsEditorProps) {
  return (
    <>
      {Object.values(UserFeature).map((feature) => {
        const featureControl = props.featureFlagsControls.controls[feature];
        const featureFlag = props.defaultFeatureFlags[feature];

        let extraLabel = "";
        switch (featureControl) {
          case FeatureControl.ALWAYS_ON:
            extraLabel = "Cannot disable, because this feature is necessary";
            break;
          case FeatureControl.ALWAYS_OFF_HOSTING:
            extraLabel = `Cannot enable, due to the hosting mode being ${hostingName(
              props.hosting,
            )}`;
            break;
          case FeatureControl.ALWAYS_OFF_TECH:
            extraLabel = "Cannot enable, due to Thrive technical issues";
            break;
          case FeatureControl.USER:
            break;
        }

        return (
          <FormControl key={feature} fullWidth>
            <FormControlLabel
              control={
                <Tooltip title={extraLabel}>
                  <span>
                    <Switch
                      name={props.name}
                      value={feature}
                      readOnly={
                        !props.inputsEnabled ||
                        featureControlImpliesReadonly(featureControl)
                      }
                      disabled={
                        !props.inputsEnabled ||
                        featureControlImpliesReadonly(featureControl)
                      }
                      defaultChecked={featureFlag}
                    />
                    {featureControl === FeatureControl.ALWAYS_ON && (
                      <input type="hidden" name={props.name} value={feature} />
                    )}
                  </span>
                </Tooltip>
              }
              label={
                <Tooltip title={extraLabel}>
                  <span>
                    {userFeatureName(feature as UserFeature)}{" "}
                    <DocsHelp
                      size="small"
                      subject={userFeatureToDocsHelpSubject(
                        feature as UserFeature,
                      )}
                    />
                  </span>
                </Tooltip>
              }
            />
          </FormControl>
        );
      })}
    </>
  );
}

interface WorkspaceFeatureFlagsEditorProps {
  name: string;
  inputsEnabled: boolean;
  featureFlagsControls: WorkspaceFeatureFlagsControls;
  defaultFeatureFlags: Record<string, boolean>;
  hosting: Hosting;
}

export function WorkspaceFeatureFlagsEditor(
  props: WorkspaceFeatureFlagsEditorProps,
) {
  return (
    <>
      {Object.values(WorkspaceFeature).map((feature) => {
        const featureControl = props.featureFlagsControls.controls[feature];
        const featureFlag = props.defaultFeatureFlags[feature];

        let extraLabel = "";
        switch (featureControl) {
          case FeatureControl.ALWAYS_ON:
            extraLabel = "Cannot disable, because this feature is necessary";
            break;
          case FeatureControl.ALWAYS_OFF_HOSTING:
            extraLabel = `Cannot enable, due to the hosting mode being ${hostingName(
              props.hosting,
            )}`;
            break;
          case FeatureControl.ALWAYS_OFF_TECH:
            extraLabel = "Cannot enable, due to Thrive technical issues";
            break;
          case FeatureControl.USER:
            break;
        }

        return (
          <FormControl key={feature} fullWidth>
            <FormControlLabel
              control={
                <Tooltip title={extraLabel}>
                  <span>
                    <Switch
                      name={props.name}
                      value={feature}
                      readOnly={
                        !props.inputsEnabled ||
                        featureControlImpliesReadonly(featureControl)
                      }
                      disabled={
                        !props.inputsEnabled ||
                        featureControlImpliesReadonly(featureControl)
                      }
                      defaultChecked={featureFlag}
                    />
                    {featureControl === FeatureControl.ALWAYS_ON && (
                      <input type="hidden" name={props.name} value={feature} />
                    )}
                  </span>
                </Tooltip>
              }
              label={
                <Tooltip title={extraLabel}>
                  <span>
                    {workspaceFeatureName(feature as WorkspaceFeature)}{" "}
                    <DocsHelp
                      size="small"
                      subject={workspaceFeatureToDocsHelpSubject(
                        feature as WorkspaceFeature,
                      )}
                    />
                  </span>
                </Tooltip>
              }
            />
          </FormControl>
        );
      })}
    </>
  );
}
