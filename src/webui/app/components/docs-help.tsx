import HelpCenterIcon from "@mui/icons-material/HelpCenter";
import { IconButton } from "@mui/material";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";

export enum DocsHelpSubject {
  ROOT,
  GAMIFICATION,
  INBOX_TASKS,
  HABITS,
  CHORES,
  BIG_PLANS,
  VACATIONS,
  PROJECTS,
  SMART_LISTS,
  METRICS,
  PERSONS,
  SLACK_TASKS,
  EMAIL_TASKS,
}

interface DocsHelpProps {
  size: "small" | "medium" | "large";
  subject: DocsHelpSubject;
}

export function DocsHelp(props: DocsHelpProps) {
  const globalProperties = useContext(GlobalPropertiesContext);

  const helpUrl = new URL(
    subjectToUrl(props.subject),
    globalProperties.docsUrl
  );

  return (
    <IconButton
      component={"a"}
      size={props.size}
      disableRipple
      color="inherit"
      href={helpUrl.toString()}
      target="_blank"
    >
      <HelpCenterIcon fontSize={props.size} />
    </IconButton>
  );
}

function subjectToUrl(subject: DocsHelpSubject) {
  switch (subject) {
    case DocsHelpSubject.ROOT:
      return `/`;
    case DocsHelpSubject.GAMIFICATION:
      return `concepts/gamification/`;
    case DocsHelpSubject.INBOX_TASKS:
      return `concepts/inbox-tasks/`;
    case DocsHelpSubject.HABITS:
      return `concepts/habits/`;
    case DocsHelpSubject.CHORES:
      return `concepts/chores/`;
    case DocsHelpSubject.BIG_PLANS:
      return `concepts/big-plans/`;
    case DocsHelpSubject.VACATIONS:
      return `concepts/vacations/`;
    case DocsHelpSubject.PROJECTS:
      return `concepts/projects/`;
    case DocsHelpSubject.SMART_LISTS:
      return `concepts/smart-lists/`;
    case DocsHelpSubject.METRICS:
      return `concepts/metrics/`;
    case DocsHelpSubject.PERSONS:
      return `concepts/persons/`;
    case DocsHelpSubject.SLACK_TASKS:
      return `concepts/slack-tasks/`;
    case DocsHelpSubject.EMAIL_TASKS:
      return `concepts/email-tasks/`;
  }
}
