import { Alert, AlertTitle } from "@mui/material";
import type { ThrownResponse } from "@remix-run/react";
import { useCatch } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";

export function makeCatchBoundary(labelFn: (c: ThrownResponse) => string) {
  function CatchBoundary() {
    const caught = useCatch();

    if (caught.status === StatusCodes.NOT_FOUND) {
      return (
        <Alert severity="warning">
          <AlertTitle>Error</AlertTitle>
          {labelFn(caught)}
        </Alert>
      );
    }

    throw new Error(`Unhandled error: ${caught.status}`);
  }

  return CatchBoundary;
}
