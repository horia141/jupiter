import { Alert, AlertTitle } from "@mui/material";
import type { ThrownResponse } from "@remix-run/react";
import { useCatch } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { BranchPanel } from "./layout/branch-panel";
import { LeafPanel } from "./layout/leaf-panel";
import { TrunkPanel } from "./layout/trunk-panel";

export function makeLeafCatchBoundary(
  returnLocation: string | (() => string),
  labelFn: (c: ThrownResponse) => string,
) {
  function CatchBoundary() {
    const caught = useCatch();

    if (caught.status === StatusCodes.NOT_FOUND) {
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
            {labelFn(caught)}
          </Alert>
        </LeafPanel>
      );
    }

    throw new Error(`Unhandled error: ${caught.status}`);
  }

  return CatchBoundary;
}

export function makeBranchCatchBoundary(
  returnLocation: string,
  labelFn: (c: ThrownResponse) => string,
) {
  function CatchBoundary() {
    const caught = useCatch();

    if (caught.status === StatusCodes.NOT_FOUND) {
      return (
        <BranchPanel
          key="error"
          inputsEnabled={true}
          returnLocation={returnLocation}
        >
          <Alert severity="warning">
            <AlertTitle>Error</AlertTitle>
            {labelFn(caught)}
          </Alert>
        </BranchPanel>
      );
    }

    throw new Error(`Unhandled error: ${caught.status}`);
  }

  return CatchBoundary;
}

export function makeTrunkCatchBoundary(
  returnLocation: string,
  labelFn: (c: ThrownResponse) => string,
) {
  function CatchBoundary() {
    const caught = useCatch();

    if (caught.status === StatusCodes.NOT_FOUND) {
      return (
        <TrunkPanel key="error" returnLocation={returnLocation}>
          <Alert severity="warning">
            <AlertTitle>Error</AlertTitle>
            {labelFn(caught)}
          </Alert>
        </TrunkPanel>
      );
    }

    throw new Error(`Unhandled error: ${caught.status}`);
  }

  return CatchBoundary;
}
