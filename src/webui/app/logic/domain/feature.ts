import {
  FeatureControl,
  UserFeature,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import { DocsHelpSubject } from "~/components/docs-help";

export function userFeatureName(feature: UserFeature): string {
  switch (feature) {
    case UserFeature.GAMIFICATION:
      return "Gamification";
  }
}

export function userFeatureToDocsHelpSubject(
  feature: UserFeature
): DocsHelpSubject {
  switch (feature) {
    case UserFeature.GAMIFICATION:
      return DocsHelpSubject.GAMIFICATION;
  }
}

export function workspaceFeatureName(feature: WorkspaceFeature): string {
  switch (feature) {
    case WorkspaceFeature.INBOX_TASKS:
      return "Inbox Tasks";
    case WorkspaceFeature.WORKING_MEM:
      return "Working Mem";
    case WorkspaceFeature.TIME_PLANS:
      return "Time Plans";
    case WorkspaceFeature.HABITS:
      return "Habits";
    case WorkspaceFeature.CHORES:
      return "Chores";
    case WorkspaceFeature.BIG_PLANS:
      return "Big Plans";
    case WorkspaceFeature.JOURNALS:
      return "Journals";
    case WorkspaceFeature.DOCS:
      return "Docs";
    case WorkspaceFeature.VACATIONS:
      return "Vacations";
    case WorkspaceFeature.PROJECTS:
      return "Projects";
    case WorkspaceFeature.SMART_LISTS:
      return "Smart Lists";
    case WorkspaceFeature.METRICS:
      return "Metrics";
    case WorkspaceFeature.PERSONS:
      return "Persons";
    case WorkspaceFeature.SLACK_TASKS:
      return "Slack Tasks";
    case WorkspaceFeature.EMAIL_TASKS:
      return "Email Tasks";
  }
}

export function workspaceFeatureToDocsHelpSubject(
  feature: WorkspaceFeature
): DocsHelpSubject {
  switch (feature) {
    case WorkspaceFeature.INBOX_TASKS:
      return DocsHelpSubject.INBOX_TASKS;
    case WorkspaceFeature.WORKING_MEM:
      return DocsHelpSubject.WORKING_MEM;
    case WorkspaceFeature.TIME_PLANS:
      return DocsHelpSubject.TIME_PLANS;
    case WorkspaceFeature.HABITS:
      return DocsHelpSubject.HABITS;
    case WorkspaceFeature.CHORES:
      return DocsHelpSubject.CHORES;
    case WorkspaceFeature.BIG_PLANS:
      return DocsHelpSubject.BIG_PLANS;
    case WorkspaceFeature.JOURNALS:
      return DocsHelpSubject.JOURNALS;
    case WorkspaceFeature.DOCS:
      return DocsHelpSubject.DOCS;
    case WorkspaceFeature.VACATIONS:
      return DocsHelpSubject.VACATIONS;
    case WorkspaceFeature.PROJECTS:
      return DocsHelpSubject.PROJECTS;
    case WorkspaceFeature.SMART_LISTS:
      return DocsHelpSubject.SMART_LISTS;
    case WorkspaceFeature.METRICS:
      return DocsHelpSubject.METRICS;
    case WorkspaceFeature.PERSONS:
      return DocsHelpSubject.PERSONS;
    case WorkspaceFeature.SLACK_TASKS:
      return DocsHelpSubject.SLACK_TASKS;
    case WorkspaceFeature.EMAIL_TASKS:
      return DocsHelpSubject.EMAIL_TASKS;
  }
}

export function featureControlImpliesReadonly(
  featureControl: FeatureControl
): boolean {
  return featureControl !== FeatureControl.USER;
}
