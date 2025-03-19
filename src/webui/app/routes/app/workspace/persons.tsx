import { WorkspaceFeature } from "@jupiter/webapi-client";
import TuneIcon from "@mui/icons-material/Tune";
import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultyTag } from "~/components/difficulty-tag";
import { DocsHelpSubject } from "~/components/docs-help";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { PeriodTag } from "~/components/period-tag";
import { PersonBirthdayTag } from "~/components/person-birthday-tag";
import { PersonRelationshipTag } from "~/components/person-relationship-tag";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const body = await apiClient.persons.personFind({
    allow_archived: false,
    include_catch_up_inbox_tasks: false,
    include_birthday_inbox_tasks: false,
    include_birthday_time_event_blocks: false,
    include_notes: false,
  });

  return json({
    entries: body.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Persons() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const isBigScreen = useBigScreen();

  return (
    <TrunkPanel
      key={"persons"}
      createLocation="/app/workspace/persons/new"
      extraControls={[
        <>
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <>
              <Button
                variant="outlined"
                to={`/app/workspace/persons/settings`}
                component={Link}
                startIcon={<TuneIcon />}
              >
                {isBigScreen ? "Settings" : ""}
              </Button>
            </>
          )}
        </>,
      ]}
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {loaderData.entries.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no persons to show. You can create a new person."
            newEntityLocations="/app/workspace/persons/new"
            helpSubject={DocsHelpSubject.PERSONS}
          />
        )}

        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              entityId={`person-${entry.person.ref_id}`}
              key={`person-${entry.person.ref_id}`}
            >
              <EntityLink to={`/app/workspace/persons/${entry.person.ref_id}`}>
                <EntityNameComponent name={entry.person.name} />
                <PersonRelationshipTag
                  relationship={entry.person.relationship}
                />
                {entry.person.birthday && (
                  <PersonBirthdayTag birthday={entry.person.birthday} />
                )}
                {entry.person.catch_up_params && (
                  <>
                    <PeriodTag period={entry.person.catch_up_params.period} />
                    {entry.person.catch_up_params.eisen && (
                      <EisenTag eisen={entry.person.catch_up_params.eisen} />
                    )}
                    {entry.person.catch_up_params.difficulty && (
                      <DifficultyTag
                        difficulty={entry.person.catch_up_params.difficulty}
                      />
                    )}
                  </>
                )}
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwareBlock>
      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary(
  "/app/workspace",
  () => `There was an error loading the persons! Please try again!`
);
