import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import type { Journal, ReportPeriodResult } from "jupiter-gen";
import {
  RecurringTaskPeriod,
  UserFeature,
  WorkspaceFeature,
} from "jupiter-gen";
import type { JournalFindResultEntry } from "jupiter-gen/dist/models/JournalFindResultEntry";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { JournalSourceTag } from "~/components/journal-source-tag";
import { PeriodTag } from "~/components/period-tag";
import { sortJournalsNaturally } from "~/logic/domain/journal";
import { isUserFeatureAvailable } from "~/logic/domain/user";
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
  const response = await getLoggedInApiClient(session).journals.journalFind({
    allow_archived: false,
    include_notes: false,
    include_writing_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Journals() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedJournals = sortJournalsNaturally(entries.map((e) => e.journal));
  const entriesByRefId = new Map<string, JournalFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.journal.ref_id, entry);
  }

  const archiveJournalFetch = useFetcher();

  function archiveJournal(journal: Journal) {
    archiveJournalFetch.submit(
      {
        intent: "archive",
      },
      {
        method: "post",
        action: `/workspace/journals/${journal.ref_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      createLocation="/workspace/journals/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedJournals.map((journal) => {
            const entry = entriesByRefId.get(
              journal.ref_id
            ) as JournalFindResultEntry;
            return (
              <EntityCard
                key={entry.journal.ref_id}
                allowSwipe
                allowMarkNotDone
                onMarkNotDone={() => archiveJournal(entry.journal)}
              >
                <EntityLink to={`/workspace/journals/${entry.journal.ref_id}`}>
                  <EntityNameComponent name={entry.journal.name} />
                  <JournalSourceTag source={entry.journal.source} />
                  <PeriodTag period={entry.journal.period} />
                  {isUserFeatureAvailable(
                    topLevelInfo.user,
                    UserFeature.GAMIFICATION
                  ) && (
                    <GamificationTag
                      period={entry.journal.period}
                      report={entry.journal.report}
                    />
                  )}
                  {
                    entry.journal.report.global_inbox_tasks_summary.done
                      .total_cnt
                  }{" "}
                  tasks done
                  {isWorkspaceFeatureAvailable(
                    topLevelInfo.workspace,
                    WorkspaceFeature.BIG_PLANS
                  ) && (
                    <>
                      {" "}
                      and{" "}
                      {
                        entry.journal.report.global_big_plans_summary.done_cnt
                      }{" "}
                      big plans done
                    </>
                  )}
                </EntityLink>
              </EntityCard>
            );
          })}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the journals! Please try again!`
);

interface GamificationTagProps {
  period: RecurringTaskPeriod;
  report: ReportPeriodResult;
}

function GamificationTag({ period, report }: GamificationTagProps) {
  if (!report.user_score_overview) {
    return null;
  }

  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return (
        <>{report.user_score_overview.daily_score.total_score} points from </>
      );
    case RecurringTaskPeriod.WEEKLY:
      return (
        <>{report.user_score_overview.weekly_score.total_score} points from </>
      );
    case RecurringTaskPeriod.MONTHLY:
      return (
        <>{report.user_score_overview.monthly_score.total_score} points from </>
      );
    case RecurringTaskPeriod.QUARTERLY:
      return (
        <>
          {report.user_score_overview.quarterly_score.total_score} points from{" "}
        </>
      );
    case RecurringTaskPeriod.YEARLY:
      return (
        <>{report.user_score_overview.yearly_score.total_score} points from </>
      );
  }
}
