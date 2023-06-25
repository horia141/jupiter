import { Divider, Stack, Typography } from "@mui/material";
import { AnimatePresence, motion } from "framer-motion";
import type { InboxTask } from "jupiter-gen";
import type {
  InboxTaskOptimisticState,
  InboxTaskParent,
} from "~/logic/domain/inbox-task";
import type { InboxTaskShowOptions } from "./inbox-task-card";
import { InboxTaskCard } from "./inbox-task-card";

interface InboxTaskStackProps {
  showLabel?: boolean;
  showOptions: InboxTaskShowOptions;
  label?: string;
  inboxTasks: InboxTask[];
  optimisticUpdates?: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId?: {
    [key: string]: InboxTaskParent;
  };
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
          <Stack spacing={2} useFlexGap>
            {props.showLabel && (
              <Divider style={{ paddingTop: "0.5rem" }}>
                <Typography variant="h6">{props.label}</Typography>
              </Divider>
            )}

            <AnimatePresence>
              {props.inboxTasks.map((it) => (
                <InboxTaskCard
                  key={it.ref_id.the_id}
                  allowSwipe={true}
                  showOptions={props.showOptions}
                  inboxTask={it}
                  optimisticState={props.optimisticUpdates?.[it.ref_id.the_id]}
                  parent={props.moreInfoByRefId?.[it.ref_id.the_id]}
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
