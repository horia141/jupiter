import { Feature, FeatureControl } from "jupiter-gen";
import { DocsHelpSubject } from "~/components/docs-help";

export function featureName(feature: Feature): string {
  switch (feature) {
    case Feature.INBOX_TASKS:
      return "Inbox Tasks";
    case Feature.HABITS:
      return "Habits";
    case Feature.CHORES:
      return "Chores";
    case Feature.BIG_PLANS:
      return "Big Plans";
    case Feature.VACATIONS:
      return "Vacations";
    case Feature.PROJECTS:
      return "Projects";
    case Feature.SMART_LISTS:
      return "Smart Lists";
    case Feature.METRICS:
      return "Metrics";
    case Feature.PERSONS:
      return "Persons";
    case Feature.SLACK_TASKS:
      return "Slack Tasks";
    case Feature.EMAIL_TASKS:
      return "Email Tasks";
  }
}

export function featureToDocsHelpSubject(feature: Feature): DocsHelpSubject {
    switch (feature) {
      case Feature.INBOX_TASKS:
        return DocsHelpSubject.INBOX_TASKS;
      case Feature.HABITS:
        return DocsHelpSubject.HABITS;
      case Feature.CHORES:
        return DocsHelpSubject.CHORES;
      case Feature.BIG_PLANS:
        return DocsHelpSubject.BIG_PLANS;
      case Feature.VACATIONS:
        return DocsHelpSubject.VACATIONS;
      case Feature.PROJECTS:
        return DocsHelpSubject.PROJECTS;
      case Feature.SMART_LISTS:
        return DocsHelpSubject.SMART_LISTS;
      case Feature.METRICS:
        return DocsHelpSubject.METRICS;
      case Feature.PERSONS:
        return DocsHelpSubject.PERSONS;
      case Feature.SLACK_TASKS:
        return DocsHelpSubject.SLACK_TASKS;
      case Feature.EMAIL_TASKS:
        return DocsHelpSubject.EMAIL_TASKS;
    }
  }

export function featureControlImpliesReadonly(
  featureControl: FeatureControl
): boolean {
  return featureControl != FeatureControl.USER;
}
