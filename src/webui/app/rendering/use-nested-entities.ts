import { UIMatch, useMatches } from "@remix-run/react";

export enum DisplayType {
  ROOT,
  TRUNK,
  BRANCH,
  LEAF,
  LEAFLET,
  TOOL,
}

function checkMatchIs(match: UIMatch, displayType: DisplayType): boolean {
  return (
    typeof match.handle === "object" &&
    match.handle !== null &&
    "displayType" in match.handle &&
    match.handle.displayType === displayType
  );
}

export function useRootNeedsToShowTrunk() {
  const matches = useMatches();

  for (const match of [...matches].reverse()) {
    if (checkMatchIs(match, DisplayType.TRUNK)) {
      return true;
    }
  }

  return false;
}

export function useBranchNeedsToShowLeaf() {
  const matches = useMatches();
  const lastMatch = matches[matches.length - 1];

  if (checkMatchIs(lastMatch, DisplayType.LEAF)) {
    return true;
  }
  return false;
}

export function useTrunkNeedsToShowBranch() {
  const matches = useMatches();

  for (const match of [...matches].reverse()) {
    if (checkMatchIs(match, DisplayType.BRANCH)) {
      return true;
    }
  }

  return false;
}

export function useTrunkNeedsToShowLeaf() {
  return useBranchNeedsToShowLeaf();
}

export function useLeafNeedsToShowLeaflet() {
  const matches = useMatches();
  const lastMatch = matches[matches.length - 1];

  if (checkMatchIs(lastMatch, DisplayType.LEAFLET)) {
    return true;
  }
  
  return false;
}
