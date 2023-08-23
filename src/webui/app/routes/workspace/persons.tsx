import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  ShouldRevalidateFunction,
  useFetcher,
  useOutlet,
} from "@remix-run/react";
import type { Person } from "jupiter-gen";
import { PersonRelationship, WorkspaceFeature } from "jupiter-gen";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
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
  const body = await getLoggedInApiClient(session).person.findPerson({
    allow_archived: false,
    include_catch_up_inbox_tasks: false,
    include_birthday_inbox_tasks: false,
  });

  return json({
    entries: body.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Persons() {
  const outlet = useOutlet();
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
        action: `/workspace/persons/${person.ref_id.the_id}`,
      }
    );
  }

  return (
    <TrunkCard>
      <NestingAwarePanel showOutlet={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          <ButtonGroup>
            <Button
              variant="contained"
              to={`/workspace/persons/new`}
              component={Link}
            >
              Create
            </Button>
            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <Button
                variant="outlined"
                to={`/workspace/persons/settings`}
                component={Link}
              >
                Settings
              </Button>
            )}
          </ButtonGroup>
        </ActionHeader>

        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={entry.person.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archivePerson(entry.person)}
            >
              <EntityLink
                to={`/workspace/persons/${entry.person.ref_id.the_id}`}
              >
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
      </NestingAwarePanel>
      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the persons! Please try again!`
);
