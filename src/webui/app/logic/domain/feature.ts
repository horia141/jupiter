import { Feature, FeatureControl } from "jupiter-gen";

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

export function featureControlImpliesReadonly(
  featureControl: FeatureControl
): boolean {
  return featureControl != FeatureControl.USER;
}
