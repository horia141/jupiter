import { Alert, AlertTitle, Box, Button, ButtonGroup } from "@mui/material";
import {
  Link,
  isRouteErrorResponse,
  useParams,
  useRouteError,
  useSearchParams,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";

import { GlobalPropertiesContext } from "~/global-properties-client";
import { isDevelopment } from "~/logic/domain/env";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";

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

export function makeLeafErrorBoundary<K extends z.ZodRawShape>(
  returnLocation:
    | string
    | ((
        params: z.infer<typeof paramsParser>,
        searchParams: URLSearchParams,
      ) => string),
  paramsParser: z.ZodObject<K>,
  labelsFor: {
    notFound?: (
      params: z.infer<typeof paramsParser>,
      searchParams: URLSearchParams,
    ) => string;
    error?: (
      params: z.infer<typeof paramsParser>,
      searchParams: URLSearchParams,
    ) => string;
  },
) {
  function ErrorBoundary() {
    const error = useRouteError();
    const globalProperties = useContext(GlobalPropertiesContext);
    const paramsRaw = useParams();
    const params = paramsParser.parse(paramsRaw);
    const [searchParams] = useSearchParams();
    const resolvedReturnLocation =
      typeof returnLocation === "function"
        ? returnLocation(params, searchParams)
        : returnLocation;

    if (isRouteErrorResponse(error)) {
      if (error.status === StatusCodes.NOT_FOUND) {
        const resolvedReturnLocation =
          typeof returnLocation === "function"
            ? returnLocation(params, searchParams)
            : returnLocation;
        return (
          <LeafPanel
            fakeKey="error"
            inputsEnabled={true}
            returnLocation={resolvedReturnLocation}
          >
            <Alert severity="warning">
              <AlertTitle>Error</AlertTitle>
              {labelsFor.notFound
                ? labelsFor.notFound(params, searchParams)
                : "Could not find entity!"}
            </Alert>
          </LeafPanel>
        );
      }
    }

    if (error instanceof Error) {
      return (
        <LeafPanel
          fakeKey="error"
          inputsEnabled={true}
          returnLocation={resolvedReturnLocation}
        >
          <Alert severity="error">
            <AlertTitle>Danger</AlertTitle>
            {labelsFor.error
              ? labelsFor.error(params, searchParams)
              : "Error retrieving entity!"}

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
        fakeKey="error"
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

export function makeBranchErrorBoundary<K extends z.ZodRawShape>(
  returnLocation:
    | string
    | ((
        params: z.infer<typeof paramsParser>,
        searchParams: URLSearchParams,
      ) => string),
  paramsParser: z.ZodObject<K>,
  labelsFor: {
    notFound?: (
      params: z.infer<typeof paramsParser>,
      searchParams: URLSearchParams,
    ) => string;
    error?: (
      params: z.infer<typeof paramsParser>,
      searchParams: URLSearchParams,
    ) => string;
  },
) {
  function ErrorBoundary() {
    const error = useRouteError();
    const globalProperties = useContext(GlobalPropertiesContext);
    const paramsRaw = useParams();
    const params = paramsParser.parse(paramsRaw);
    const [searchParams] = useSearchParams();
    const resolvedReturnLocation =
      typeof returnLocation === "function"
        ? returnLocation(params, searchParams)
        : returnLocation;

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
                ? labelsFor.notFound(params, searchParams)
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
            {labelsFor.error
              ? labelsFor.error(params, searchParams)
              : "Error retrieving entity!"}

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

    if (error instanceof Error) {
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

    return (
      <ToolPanel key="error">
        <Alert severity="error">
          <AlertTitle>Critical</AlertTitle>
          Unknown error!
        </Alert>
      </ToolPanel>
    );
  }

  return ErrorBoundary;
}
