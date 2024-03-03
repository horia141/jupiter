import TuneIcon from "@mui/icons-material/Tune";
import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import type { Person } from "jupiter-gen";
import { PersonRelationship, WorkspaceFeature } from "jupiter-gen";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { PeriodTag } from "~/components/period-tag";
import { PersonBirthdayTag } from "~/components/person-birthday-tag";
import { PersonRelationshipTag } from "~/components/person-relationship-tag";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const body = await getLoggedInApiClient(session).persons.personFind({
    allow_archived: false,
    include_catch_up_inbox_tasks: false,
    include_birthday_inbox_tasks: false,
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

  const archivePersonFetch = useFetcher();

  function archivePerson(person: Person) {
    archivePersonFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
        relationship: PersonRelationship.OTHER,
      },
      {
        method: "post",
        action: `/workspace/persons/${person.ref_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      createLocation="/workspace/persons/new"
      extraControls={[
        <>
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <>
              <Button
                variant="outlined"
                to={`/workspace/persons/settings`}
                component={Link}
                startIcon={<TuneIcon />}
              >
                Settings
              </Button>
            </>
          )}
        </>,
      ]}
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={entry.person.ref_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archivePerson(entry.person)}
            >
              <EntityLink to={`/workspace/persons/${entry.person.ref_id}`}>
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the persons! Please try again!`
);
