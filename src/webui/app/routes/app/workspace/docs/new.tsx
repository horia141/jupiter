import { FormControl } from "@mui/material";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useNavigation } from "@remix-run/react";
import { z } from "zod";

import { DocEditor } from "~/components/domain/concept/doc/doc-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = z.object({});

export const handle = {
  displayType: DisplayType.LEAF,
};

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function NewDoc() {
  const navigation = useNavigation();

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key="docs/new"
      fakeKey={"docs/new"}
      returnLocation="/app/workspace/docs"
      inputsEnabled={inputsEnabled}
      initialExpansionState={LeafPanelExpansionState.FULL}
    >
      <SectionCard title="New Doc" actionsPosition={ActionsPosition.BELOW}>
        <FormControl fullWidth>
          <DocEditor inputsEnabled={inputsEnabled} />
        </FormControl>
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/docs",
  ParamsSchema,
  {
    notFound: () => `Could not find the document!`,
    error: () => `There was an error creating the document! Please try again!`,
  },
);
