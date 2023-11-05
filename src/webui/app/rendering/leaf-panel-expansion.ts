import { z } from "zod";

export enum LeafCardExpansionState {
  SMALL = "small",
  MEDIUM = "medium",
  LARGE = "large",
  FULL = "full",
}

export function saveLeafPanelExpansion(
  entityRoot: string,
  expansionState: LeafCardExpansionState
) {
  window.sessionStorage.setItem(
    `leaf-panel-expansion:${entityRoot}`,
    expansionState
  );
}

export function loadLeafPanelExpansion(
  entityRoot: string
): LeafCardExpansionState | null {
  const expansionStr = window.sessionStorage.getItem(
    `leaf-panel-expansion:${entityRoot}`
  );
  return z.nativeEnum(LeafCardExpansionState).or(z.null()).parse(expansionStr);
}
