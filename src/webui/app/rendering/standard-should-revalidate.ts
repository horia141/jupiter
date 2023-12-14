import { ShouldRevalidateFunction } from "@remix-run/react";

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

  if (formAction === "/workspace/notes/update") {
    return false;
  }

  if (formAction === "/workspace/notes/update-for-entity") {
    return false;
  }

  return defaultShouldRevalidate;
};
