import { useMatches } from "@remix-run/react";

export enum DisplayType {
  ROOT,
  TRUNK,
  BRANCH,
  LEAF,
}

export function useRootNeedsToShowTrunk() {
  const matches = useMatches();

  for (const match of [...matches].reverse()) {
    if (match.handle && match.handle.displayType) {
      if (match.handle.displayType === DisplayType.TRUNK) {
        return true;
      }
    }
  }

  return false;
}

export function useBranchNeedsToShowLeaf() {
  const matches = useMatches();
  const lastMatch = matches[matches.length - 1];

  if (lastMatch.handle && lastMatch.handle.displayType) {
    if (lastMatch.handle.displayType === DisplayType.LEAF) {
      return true;
    }
  }

  return false;
}

export function useTrunkNeedsToShowBranch() {
  const matches = useMatches();

  for (const match of [...matches].reverse()) {
    if (match.handle && match.handle.displayType) {
      if (match.handle.displayType === DisplayType.BRANCH) {
        return true;
      }
    }
  }

  return false;
}

export function useTrunkNeedsToShowLeaf() {
  return useBranchNeedsToShowLeaf();
}

export function useOutWhatIsVisibleNext(nestedMatcher: RegExp): DisplayType {
  const matches = useMatches();
  const lastMatch = matches[matches.length - 1];

  if (lastMatch.pathname.endsWith("/settings")) {
    return DisplayType.LEAF;
  } else if (lastMatch.pathname.endsWith("/details")) {
    return DisplayType.LEAF;
  } else if (lastMatch.pathname.endsWith("/new")) {
    return DisplayType.LEAF;
  } else if (lastMatch.pathname.match(nestedMatcher) !== null) {
    return DisplayType.BRANCH;
  } else {
    return DisplayType.TRUNK;
  }
}
