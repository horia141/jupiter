import { Alert, AlertTitle, Box, Button, ButtonGroup } from "@mui/material";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { isDevelopment } from "~/logic/domain/env";
import { BranchPanel } from "./layout/branch-panel";
import { LeafPanel } from "./layout/leaf-panel";
import { ToolPanel } from "./layout/tool-panel";
import { TrunkPanel } from "./layout/trunk-panel";
import { isRouteErrorResponse, Link, useRouteError } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";

export function makeRootErrorBoundary(labelsFor: { error?: () => string }) {
  function ErrorBoundary() {
    const error = useRouteError();
    const globalProperties = useContext(GlobalPropertiesContext);

    if (isRouteErrorResponse(error)) {
      if (error.status === 426 /* UPGRADE RE  QUIRED */) {
        return (
          <Alert severity="warning">
            <AlertTitle>Your session has expired! Login again!</AlertTitle>
            <ButtonGroup>
              <Button variant="outlined" component={Link} to="/app/login">
                Login
              </Button>
            </ButtonGroup>
          </Alert>
        );
      }
    }

    if (error instanceof Error) {
      return (
        <Alert severity="error">
          <AlertTitle>Danger</AlertTitle>
          {labelsFor.error ? labelsFor.error() : "Error retrieving entity!"}

          {isDevelopment(globalProperties.env) && (
            <Box>
              <pre>{error.message}</pre>
              <pre>{error.stack}</pre>
            </Box>
          )}
        </Alert>
      );
    }

    return (
      <Alert severity="error">
        <AlertTitle>Critical</AlertTitle>
        Unknown error!
      </Alert>
    );
  }

  return ErrorBoundary;
}

export function makeLeafErrorBoundary(
  returnLocation: string | (() => string),
  labelsFor: {
    notFound?: () => string;
    error?: () => string;
  },
) {
  function ErrorBoundary() {
    const error = useRouteError();
    const globalProperties = useContext(GlobalPropertiesContext);
    const resolvedReturnLocation =
      typeof returnLocation === "function" ? returnLocation() : returnLocation;

    if (isRouteErrorResponse(error)) {
      if (error.status === StatusCodes.NOT_FOUND) {
        const resolvedReturnLocation =
          typeof returnLocation === "function"
            ? returnLocation()
            : returnLocation;
        return (
          <LeafPanel
            key="error"
            inputsEnabled={true}
            returnLocation={resolvedReturnLocation}
          >
            <Alert severity="warning">
              <AlertTitle>Error</AlertTitle>
              {labelsFor.notFound
                ? labelsFor.notFound()
                : "Could not find entity!"}
            </Alert>
          </LeafPanel>
        );
      }
    }

    if (error instanceof Error) {
      return (
        <LeafPanel
          key="error"
          inputsEnabled={true}
          returnLocation={resolvedReturnLocation}
        >
          <Alert severity="error">
            <AlertTitle>Danger</AlertTitle>
            {labelsFor.error ? labelsFor.error() : "Error retrieving entity!"}

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

    return (
      <LeafPanel
        key="error"
        inputsEnabled={true}
        returnLocation={resolvedReturnLocation}
      >
        <Alert severity="error">
          <AlertTitle>Critical</AlertTitle>
          Unknown error!
        </Alert>
      </LeafPanel>
    );
  }

  return ErrorBoundary;
}

export function makeBranchErrorBoundary(
  returnLocation: string | (() => string),
  labelsFor: {
    notFound?: () => string;
    error?: () => string;
  },
) {
  function ErrorBoundary() {
    const error = useRouteError();
    const globalProperties = useContext(GlobalPropertiesContext);
    const resolvedReturnLocation =
      typeof returnLocation === "function" ? returnLocation() : returnLocation;

    if (isRouteErrorResponse(error)) {
      if (error.status === StatusCodes.NOT_FOUND) {
        return (
          <BranchPanel
            key="error"
            inputsEnabled={true}
            returnLocation={resolvedReturnLocation}
          >
            <Alert severity="warning">
              <AlertTitle>Error</AlertTitle>
              {labelsFor.notFound
                ? labelsFor.notFound()
                : "Could not find entity!"}
            </Alert>
          </BranchPanel>
        );
      }
    }

    if (error instanceof Error) {
      return (
        <BranchPanel
          key="error"
          inputsEnabled={true}
          returnLocation={resolvedReturnLocation}
        >
          <Alert severity="error">
            <AlertTitle>Danger</AlertTitle>
            {labelsFor.error ? labelsFor.error() : "Error retrieving entity!"}

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

    return (
      <BranchPanel
        key="error"
        inputsEnabled={true}
        returnLocation={resolvedReturnLocation}
      >
        <Alert severity="error">
          <AlertTitle>Critical</AlertTitle>
          Unknown error!
        </Alert>
      </BranchPanel>
    );
  }

  return ErrorBoundary;
}

export function makeTrunkErrorBoundary(
  returnLocation: string,
  labelsFor: {
    error?: () => string;
  },
) {
  function ErrorBoundary() {
    const error = useRouteError();
    const globalProperties = useContext(GlobalPropertiesContext);

    if (error instanceof Error) {
      return (
        <TrunkPanel key="error" returnLocation={returnLocation}>
          <Alert severity="error">
            <AlertTitle>Danger</AlertTitle>
            {labelsFor.error ? labelsFor.error() : "Error retrieving entity!"}

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

    return (
      <TrunkPanel key="error" returnLocation={returnLocation}>
        <Alert severity="error">
          <AlertTitle>Critical</AlertTitle>
          Unknown error!
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
