import { Alert, AlertTitle, Box } from "@mui/material";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { isDevelopment } from "~/logic/domain/env";
import { BranchPanel } from "./layout/branch-panel";
import { LeafPanel } from "./layout/leaf-panel";
import { ToolPanel } from "./layout/tool-panel";
import { TrunkPanel } from "./layout/trunk-panel";

export function makeRootErrorBoundary(labelFn: () => string) {
  function ErrorBoundary({ error }: { error: Error }) {
    const globalProperties = useContext(GlobalPropertiesContext);

    return (
      <Alert severity="error">
        <AlertTitle>Danger</AlertTitle>
        {labelFn()}

        {isDevelopment(globalProperties.env) && (
          <Box>
            <pre>{error.message}</pre>
            <pre>{error.stack}</pre>
          </Box>
        )}
      </Alert>
    );
  }

  return ErrorBoundary;
}

export function makeLeafErrorBoundary(
  returnLocation: string | (() => string),
  labelFn: () => string,
) {
  function ErrorBoundary({ error }: { error: Error }) {
    const globalProperties = useContext(GlobalPropertiesContext);
    const resolvedReturnLocation =
      typeof returnLocation === "function" ? returnLocation() : returnLocation;

    return (
      <LeafPanel
        key="error"
        inputsEnabled={true}
        returnLocation={resolvedReturnLocation}
      >
        <Alert severity="error">
          <AlertTitle>Danger</AlertTitle>
          {labelFn()}

          {isDevelopment(globalProperties.env) && (
            <Box>
              <pre>{error.message}</pre>
              <pre>{error.stack}</pre>
            </Box>
          )}
        </Alert>
      </LeafPanel>
    );
  }

  return ErrorBoundary;
}

export function makeBranchErrorBoundary(
  returnLocation: string | (() => string),
  labelFn: () => string,
) {
  function ErrorBoundary({ error }: { error: Error }) {
    const globalProperties = useContext(GlobalPropertiesContext);
    const resolvedReturnLocation =
      typeof returnLocation === "function" ? returnLocation() : returnLocation;

    return (
      <BranchPanel
        key="error"
        inputsEnabled={true}
        returnLocation={resolvedReturnLocation}
      >
        <Alert severity="error">
          <AlertTitle>Danger</AlertTitle>
          {labelFn()}

          {isDevelopment(globalProperties.env) && (
            <Box>
              <pre>{error.message}</pre>
              <pre>{error.stack}</pre>
            </Box>
          )}
        </Alert>
      </BranchPanel>
    );
  }

  return ErrorBoundary;
}

export function makeTrunkErrorBoundary(
  returnLocation: string,
  labelFn: () => string,
) {
  function ErrorBoundary({ error }: { error: Error }) {
    const globalProperties = useContext(GlobalPropertiesContext);

    return (
      <TrunkPanel key="error" returnLocation={returnLocation}>
        <Alert severity="error">
          <AlertTitle>Danger</AlertTitle>
          {labelFn()}

          {isDevelopment(globalProperties.env) && (
            <Box>
              <pre>{error.message}</pre>
              <pre>{error.stack}</pre>
            </Box>
          )}
        </Alert>
      </TrunkPanel>
    );
  }

  return ErrorBoundary;
}

export function makeToolErrorBoundary(labelFn: () => string) {
  function ErrorBoundary({ error }: { error: Error }) {
    const globalProperties = useContext(GlobalPropertiesContext);

    return (
      <ToolPanel key="error">
        <Alert severity="error">
          <AlertTitle>Danger</AlertTitle>
          {labelFn()}

          {isDevelopment(globalProperties.env) && (
            <Box>
              <pre>{error.message}</pre>
              <pre>{error.stack}</pre>
            </Box>
          )}
        </Alert>
      </ToolPanel>
    );
  }

  return ErrorBoundary;
}
