import type { ShouldRevalidateFunction } from "@remix-run/react";

export const basicShouldRevalidate: ShouldRevalidateFunction = ({
  actionResult,
  currentParams,
  currentUrl,
  defaultShouldRevalidate,
  formAction,
  formData,
  formEncType,
  formMethod,
  nextParams,
  nextUrl,
}) => {
  return defaultShouldRevalidate;
};

export const standardShouldRevalidate: ShouldRevalidateFunction = ({
  actionResult,
  currentParams,
  currentUrl,
  defaultShouldRevalidate,
  formAction,
  formData,
  formEncType,
  formMethod,
  nextParams,
  nextUrl,
}) => {
  if (formAction === "/workspace/inbox-tasks/update-status-and-eisen") {
    return false;
  }

  if (formAction === "/workspace/docs/update-action") {
    return false;
  }

  if (formAction === "/workspace/core/notes/update") {
    return false;
  }

  return defaultShouldRevalidate;
};
