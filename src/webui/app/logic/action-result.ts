import { z } from "zod";

export interface NoErrorNoData {
  theType: "no-error-no-data";
}

export interface SomeErrorNoData {
  theType: "some-error-no-data";
  intent?: string;
  globalError: string | null;
  fieldErrors: { [key: string]: string };
}

export interface NoErrorSomeData<T> {
  theType: "no-error-some-data";
  data: T;
}

export type ActionResult<T> =
  | NoErrorNoData
  | SomeErrorNoData
  | NoErrorSomeData<T>;

export function noErrorNoData(): NoErrorNoData {
  return {
    theType: "no-error-no-data",
  };
}

export function noErrorSomeData<T>(data: T): ActionResult<T> {
  return {
    theType: "no-error-some-data",
    data: data,
  };
}

export function getFieldError(
  uiErrorInfo: SomeErrorNoData | undefined,
  fieldPrefix: string
): string | undefined {
  if (uiErrorInfo === undefined) {
    return undefined;
  }

  for (const [key, message] of Object.entries(uiErrorInfo.fieldErrors)) {
    if (key.startsWith(fieldPrefix)) {
      return message;
    }
  }

  return undefined;
}

const ValidationErrorSchema = z.object({
  detail: z.array(
    z.object({
      loc: z.array(z.string()),
      msg: z.string(),
    })
  ),
});

export function validationErrorToUIErrorInfo(
  errorBodyRaw: object,
  intent?: string
): SomeErrorNoData {
  const errorBody = ValidationErrorSchema.parse(errorBodyRaw);
  const detail = errorBody.detail;

  let globalError = null;
  const fieldErrors: { [key: string]: string } = {};

  for (const entry of detail) {
    if (entry.loc.length === 1 && entry.loc[0] === "body") {
      globalError = entry.msg;
    } else {
      const fieldErrorKey = ("/" + entry.loc.join("/")).replace("/body", "");
      fieldErrors[fieldErrorKey] = entry.msg;
    }
  }

  return { theType: "some-error-no-data", intent, globalError, fieldErrors };
}
