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
  if (
    currentUrl.pathname === nextUrl.pathname &&
    onlyDifferenceIsInTimeEventParamsSource(
      formMethod || "GET",
      currentUrl,
      nextUrl
    )
  ) {
    return false;
  }

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

  if (
    currentUrl.pathname === nextUrl.pathname &&
    onlyDifferenceIsInTimeEventParamsSource(
      formMethod || "GET",
      currentUrl,
      nextUrl
    )
  ) {
    return false;
  }

  return defaultShouldRevalidate;
};

function onlyDifferenceIsInTimeEventParamsSource(
  formMethod: string,
  currentUrl: URL,
  nextUrl: URL
): boolean {
  if (formMethod !== "GET") {
    return false;
  }

  const currentKeys = Array.from(currentUrl.searchParams.keys());
  const nextKeys = Array.from(nextUrl.searchParams.keys());

  if (currentKeys.length === 0 && nextKeys.length === 0) {
    return false;
  }

  for (const key of currentKeys) {
    if (
      key === "sourceStartDate" ||
      key === "sourceStartTimeInDay" ||
      key === "sourceDurationMins"
    ) {
      continue;
    }

    if (currentUrl.searchParams.get(key) !== nextUrl.searchParams.get(key)) {
      return false;
    }
  }

  for (const key of nextKeys) {
    if (
      key === "sourceStartDate" ||
      key === "sourceStartTimeInDay" ||
      key === "sourceDurationMins"
    ) {
      continue;
    }

    if (currentUrl.searchParams.get(key) !== nextUrl.searchParams.get(key)) {
      return false;
    }
  }

  return true;
}
