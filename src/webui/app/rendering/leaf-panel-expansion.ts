import { z } from "zod";

export enum LeafPanelExpansionState {
  SMALL = "small",
  MEDIUM = "medium",
  LARGE = "large",
  FULL = "full",
}

export function saveLeafPanelExpansion(
  entityRoot: string,
  expansionState: LeafPanelExpansionState
) {
  window.sessionStorage.setItem(
    `leaf-panel-expansion:${entityRoot}`,
    expansionState
  );
}

export function loadLeafPanelExpansion(
  entityRoot: string
): LeafPanelExpansionState | null {
  const expansionStr = window.sessionStorage.getItem(
    `leaf-panel-expansion:${entityRoot}`
  );
  return z.nativeEnum(LeafPanelExpansionState).or(z.null()).parse(expansionStr);
}
