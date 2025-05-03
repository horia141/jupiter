import type { InboxTask } from "@jupiter/webapi-client";
import { Stack, ToggleButton, ToggleButtonGroup } from "@mui/material";
import { Link, useLocation, useSearchParams } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import type { DateTime } from "luxon";

import type {
  InboxTaskOptimisticState,
  InboxTaskParent,
} from "~/logic/domain/inbox-task";
import type { TopLevelInfo } from "~/top-level-context";
import type { InboxTaskShowOptions } from "~/components/domain/concept/inbox-task/inbox-task-card";
import { InboxTaskCard } from "~/components/domain/concept/inbox-task/inbox-task-card";
import { StandardDivider } from "~/components/infra/standard-divider";

interface PagesProps {
  retrieveOffsetParamName: string;
  totalCnt: number;
  pageSize: number;
}

interface InboxTaskStackProps {
  today: DateTime;
  topLevelInfo: TopLevelInfo;
  showOptions: InboxTaskShowOptions;
  label?: string;
  inboxTasks: InboxTask[];
  optimisticUpdates?: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId?: {
    [key: string]: InboxTaskParent;
  };
  withPages?: PagesProps;
  onCardMarkDone?: (it: InboxTask) => void;
  onCardMarkNotDone?: (it: InboxTask) => void;
}

export function InboxTaskStack(props: InboxTaskStackProps) {
  const isEmpty = props.inboxTasks.length === 0;

  function handleMarkDone(it: InboxTask) {
    if (props.onCardMarkDone) {
      props.onCardMarkDone(it);
    }
  }

  function handleMarkNotDone(it: InboxTask) {
    if (props.onCardMarkNotDone) {
      props.onCardMarkNotDone(it);
    }
  }

  return (
    <AnimatePresence>
      {!isEmpty && (
        <motion.div
          key={props.label}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, height: "0px" }}
          transition={{ duration: 1 }}
        >
          <Stack spacing={2}>
            {props.label && (
              <StandardDivider title={props.label} size="large" />
            )}

            {props.withPages && (
              <Pages
                retrieveOffsetParamName={
                  props.withPages.retrieveOffsetParamName
                }
                totalCnt={props.withPages.totalCnt}
                pageSize={props.withPages.pageSize}
              />
            )}

            <AnimatePresence>
              {props.inboxTasks.map((it) => (
                <InboxTaskCard
                  today={props.today}
                  topLevelInfo={props.topLevelInfo}
                  key={it.ref_id}
                  allowSwipe={true}
                  showOptions={props.showOptions}
                  inboxTask={it}
                  optimisticState={props.optimisticUpdates?.[it.ref_id]}
                  parent={props.moreInfoByRefId?.[it.ref_id]}
                  onMarkDone={handleMarkDone}
                  onMarkNotDone={handleMarkNotDone}
                />
              ))}
            </AnimatePresence>
          </Stack>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Pages(props: PagesProps) {
  const pageCount = Math.ceil(props.totalCnt / props.pageSize);
  const [searchParams] = useSearchParams();
  const currentOffset = parseInt(
    searchParams.get(props.retrieveOffsetParamName) || "0",
  );
  const currentPage = Math.floor(currentOffset / props.pageSize);
  const location = useLocation();

  const shouldShowPage = Array(pageCount).fill(false);
  shouldShowPage[0] = true;
  shouldShowPage[pageCount - 1] = true;

  if (currentPage - 3 >= 0) shouldShowPage[currentPage - 3] = true;
  if (currentPage - 2 >= 0) shouldShowPage[currentPage - 2] = true;
  if (currentPage - 1 >= 0) shouldShowPage[currentPage - 1] = true;
  shouldShowPage[currentPage] = true;
  if (currentPage + 1 < pageCount) shouldShowPage[currentPage + 1] = true;
  if (currentPage + 2 < pageCount) shouldShowPage[currentPage + 2] = true;
  if (currentPage + 3 < pageCount) shouldShowPage[currentPage + 3] = true;

  const renderPageButtons = () => {
    const buttons = [];
    for (let i = 0; i < pageCount; i++) {
      if (shouldShowPage[i]) {
        const newSearchParams = new URLSearchParams(searchParams.toString());
        newSearchParams.set(
          props.retrieveOffsetParamName,
          (i * props.pageSize).toString(),
        );

        buttons.push(
          <ToggleButton
            key={i + 1}
            value={i}
            component={Link}
            to={{
              pathname: location.pathname,
              search: `?${newSearchParams.toString()}`,
            }}
          >
            {i + 1}
          </ToggleButton>,
        );
      } else if (i > 0 && shouldShowPage[i - 1]) {
        buttons.push(
          <ToggleButton key={`ellipsis-${i}`} value="ellipsis" disabled>
            ...
          </ToggleButton>,
        );
      }
    }
    return buttons;
  };

  return (
    <ToggleButtonGroup
      size="small"
      value={currentPage}
      exclusive
      sx={{ alignSelf: "center" }}
    >
      {renderPageButtons()}
    </ToggleButtonGroup>
  );
}
