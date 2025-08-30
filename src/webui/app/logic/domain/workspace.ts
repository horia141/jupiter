import type { Workspace } from "@jupiter/webapi-client";
import {
  InboxTaskSource,
  NamedEntityTag,
  WorkspaceFeature,
} from "@jupiter/webapi-client";

export function isWorkspaceFeatureAvailable(
  workspace: Workspace,
  feature: WorkspaceFeature,
): boolean {
  return workspace.feature_flags[feature];
}

export function inferEntityTagsForEnabledFeatures(
  workspace: Workspace,
  entityTags: Array<NamedEntityTag>,
): Array<NamedEntityTag> {
  // Keep in sync with python:core:infer_entity_tags_for_enabled_features
  const inferredEntityTags: Array<NamedEntityTag> = [];

  for (const entityTag of entityTags) {
    if (entityTag === NamedEntityTag.INBOX_TASK) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.WORKING_MEM &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.WORKING_MEM)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.TIME_PLAN &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.TIME_PLAN_ACTIVITY &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SCHEDULE_STREAM &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SCHEDULE_EVENT_IN_DAY &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SCHEDULE_EVENT_FULL_DAYS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.HABIT &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.HABITS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.CHORE &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.CHORES)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.BIG_PLAN &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.BIG_PLANS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.JOURNAL &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.JOURNALS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.DOC &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.DOCS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.VACATION &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.VACATIONS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.PROJECT &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PROJECTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SMART_LIST &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SMART_LISTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SMART_LIST_ITEM &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SMART_LISTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SMART_LIST_TAG &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SMART_LISTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.METRIC &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.METRICS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.METRIC_ENTRY &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.METRICS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.PERSON &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PERSONS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SLACK_TASK &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SLACK_TASKS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.EMAIL_TASK &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.EMAIL_TASKS)
    ) {
      inferredEntityTags.push(entityTag);
    }
  }

  return inferredEntityTags;
}

export function inferSourcesForEnabledFeatures(
  workspace: Workspace,
  sources: Array<InboxTaskSource>,
): Array<InboxTaskSource> {
  // Keep in sync with python:core:infer_sources_for_enabled_features
  const inferredSources: Array<InboxTaskSource> = [];

  for (const source of sources) {
    if (source === InboxTaskSource.USER) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.WORKING_MEM_CLEANUP &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.WORKING_MEM)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.TIME_PLAN &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.HABIT &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.HABITS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.CHORE &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.CHORES)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.BIG_PLAN &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.BIG_PLANS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.JOURNAL &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.JOURNALS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.METRIC &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.METRICS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.PERSON_BIRTHDAY &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PERSONS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.PERSON_CATCH_UP &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PERSONS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.SLACK_TASK &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SLACK_TASKS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.EMAIL_TASK &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.EMAIL_TASKS)
    ) {
      inferredSources.push(source);
    }
  }

  return inferredSources;
}
