import TuneIcon from "@mui/icons-material/Tune";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultyTag } from "~/components/domain/core/difficulty-tag";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EisenTag } from "~/components/domain/core/eisen-tag";
import { EntityNameComponent } from "~/components/infra/entity-name";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { PeriodTag } from "~/components/domain/core/period-tag";
import { PersonBirthdayTag } from "~/components/domain/concept/person/person-birthday-tag";
import { PersonRelationshipTag } from "~/components/domain/concept/person/person-relationship-tag";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { NavSingle, SectionActions } from "~/components/infra/section-actions";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
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

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  return (
    <TrunkPanel
      key={"persons"}
      createLocation="/app/workspace/persons/new"
      returnLocation="/app/workspace"
      actions={
        <SectionActions
          id="persons-actions"
          topLevelInfo={topLevelInfo}
          inputsEnabled={true}
          actions={[
            NavSingle({
              text: "Settings",
              link: `/app/workspace/persons/settings`,
              icon: <TuneIcon />,
            }),
          ]}
        />
      }
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeaf}
      >
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

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the persons! Please try again!`,
});
