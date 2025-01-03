import { useMatches } from "@remix-run/react";

export enum DisplayType {
  ROOT,
  TRUNK,
  BRANCH,
  LEAF,
  TOOL,
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
