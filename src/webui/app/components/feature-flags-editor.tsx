import { FormControl, FormControlLabel, Switch, Tooltip } from "@mui/material";
import {
  Feature,
  FeatureControl,
  FeatureFlagsControls,
  Hosting,
} from "jupiter-gen";
import {
  featureControlImpliesReadonly,
  featureName,
  featureToDocsHelpSubject,
} from "~/logic/domain/feature";
import { hostingName } from "~/logic/domain/hosting";
import { DocsHelp } from "./docs-help";

interface FeatureFlagsEditorProps {
  name: string;
  inputsEnabled: boolean;
  featureFlagsControls: FeatureFlagsControls;
  defaultFeatureFlags: Record<string, boolean>;
  hosting: Hosting;
}

export function FeatureFlagsEditor(props: FeatureFlagsEditorProps) {
  return (
    <>
      {Object.values(Feature).map((feature) => {
        const featureControl = props.featureFlagsControls.controls[feature];
        const featureFlag = props.defaultFeatureFlags[feature];

        let extraLabel = "";
        switch (featureControl) {
          case FeatureControl.ALWAYS_ON:
            extraLabel = "Cannot disable, because this feature is necessary";
            break;
          case FeatureControl.ALWAYS_OFF_HOSTING:
            extraLabel = `Cannot enable, due to the hosting mode being ${hostingName(
              props.hosting
            )}`;
            break;
          case FeatureControl.ALWAYS_OFF_TECH:
            extraLabel = "Cannot enable, due to Jupiter technical issues";
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
                    {featureName(feature as Feature)}{" "}
                    <DocsHelp
                      size="small"
                      subject={featureToDocsHelpSubject(feature as Feature)}
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
