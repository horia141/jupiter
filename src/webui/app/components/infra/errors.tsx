import { Alert } from "@mui/material";
import type { ActionResult } from "~/logic/action-result";
import { getFieldError } from "~/logic/action-result";

interface GlobalErrorProps {
  intent?: string;
  actionResult: ActionResult<unknown> | undefined;
}

export function GlobalError(props: GlobalErrorProps) {
  if (props.actionResult === undefined) {
    return null;
  }
  if (props.actionResult.theType !== "some-error-no-data") {
    return null;
  }
  if (props.actionResult.globalError === null) {
    return null;
  }
  if (
    props.intent !== undefined &&
    props.actionResult.intent !== props.intent
  ) {
    return null;
  }

  return <Alert severity="error">{props.actionResult.globalError}</Alert>;
}

interface FieldErrorProps {
  actionResult: ActionResult<unknown> | undefined;
  fieldName: string;
}

export function FieldError(props: FieldErrorProps) {
  if (props.actionResult === undefined) {
    return null;
  }
  if (props.actionResult.theType !== "some-error-no-data") {
    return null;
  }

  const errorMsg = getFieldError(props.actionResult, props.fieldName);

  if (errorMsg === undefined) {
    return null;
  }

  return <Alert severity="error">{errorMsg}</Alert>;
}

export function BetterFieldError(props: FieldErrorProps): {
  error?: boolean;
  helperText?: string;
} {
  if (props.actionResult === undefined) {
    return {};
  }
  if (props.actionResult.theType !== "some-error-no-data") {
    return {};
  }

  const errorMsg = getFieldError(props.actionResult, props.fieldName);

  if (errorMsg === undefined) {
    return {};
  }

  return {
    error: true,
    helperText: errorMsg,
  };
}
