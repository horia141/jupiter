import {
  Feature,
  InboxTaskSource,
  NamedEntityTag,
  SyncTarget,
  Workspace,
} from "jupiter-gen";

export function isFeatureAvailable(
  workspace: Workspace,
  feature: Feature
): boolean {
  return workspace.feature_flags[feature];
}

export function inferEntityTagsForEnabledFeatures(
  workspace: Workspace,
  entityTags: Array<NamedEntityTag>
): Array<NamedEntityTag> {
  // Keep in sync with python:core:infer_entity_tags_for_enabled_features
  const inferredEntityTags: Array<NamedEntityTag> = [];

  for (const entityTag of entityTags) {
    if (entityTag === NamedEntityTag.INBOX_TASK) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.HABIT &&
      isFeatureAvailable(workspace, Feature.HABITS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.CHORE &&
      isFeatureAvailable(workspace, Feature.CHORES)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.BIG_PLAN &&
      isFeatureAvailable(workspace, Feature.BIG_PLANS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.VACATION &&
      isFeatureAvailable(workspace, Feature.VACATIONS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.PROJECT &&
      isFeatureAvailable(workspace, Feature.PROJECTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SMART_LIST &&
      isFeatureAvailable(workspace, Feature.SMART_LISTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SMART_LIST_ITEM &&
      isFeatureAvailable(workspace, Feature.SMART_LISTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SMART_LIST_TAG &&
      isFeatureAvailable(workspace, Feature.SMART_LISTS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.METRIC &&
      isFeatureAvailable(workspace, Feature.METRICS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.METRIC_ENTRY &&
      isFeatureAvailable(workspace, Feature.METRICS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.PERSON &&
      isFeatureAvailable(workspace, Feature.PERSONS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.SLACK_TASK &&
      isFeatureAvailable(workspace, Feature.SLACK_TASKS)
    ) {
      inferredEntityTags.push(entityTag);
    } else if (
      entityTag === NamedEntityTag.EMAIL_TASK &&
      isFeatureAvailable(workspace, Feature.EMAIL_TASKS)
    ) {
      inferredEntityTags.push(entityTag);
    }
  }

  return inferredEntityTags;
}

export function inferSourcesForEnabledFeatures(
  workspace: Workspace,
  sources: Array<InboxTaskSource>
): Array<InboxTaskSource> {
  // Keep in sync with python:core:infer_sources_for_enabled_features
  const inferredSources: Array<InboxTaskSource> = [];

  for (const source of sources) {
    if (source === InboxTaskSource.USER) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.HABIT &&
      isFeatureAvailable(workspace, Feature.HABITS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.CHORE &&
      isFeatureAvailable(workspace, Feature.CHORES)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.BIG_PLAN &&
      isFeatureAvailable(workspace, Feature.BIG_PLANS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.METRIC &&
      isFeatureAvailable(workspace, Feature.METRICS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.PERSON_BIRTHDAY &&
      isFeatureAvailable(workspace, Feature.PERSONS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.PERSON_CATCH_UP &&
      isFeatureAvailable(workspace, Feature.PERSONS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.SLACK_TASK &&
      isFeatureAvailable(workspace, Feature.SLACK_TASKS)
    ) {
      inferredSources.push(source);
    } else if (
      source === InboxTaskSource.EMAIL_TASK &&
      isFeatureAvailable(workspace, Feature.EMAIL_TASKS)
    ) {
      inferredSources.push(source);
    }
  }

  return inferredSources;
}

export function inferSyncTargetsForEnabledFeatures(
  workspace: Workspace,
  syncTargets: Array<SyncTarget>
): Array<SyncTarget> {
  // Keep in sync with python:core:infer_sync_targets_for_enabled_features
  const inferredSyncTargets: Array<SyncTarget> = [];

  for (const syncTarget of syncTargets) {
    if (
      syncTarget === SyncTarget.INBOX_TASKS &&
      isFeatureAvailable(workspace, Feature.INBOX_TASKS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.HABITS &&
      isFeatureAvailable(workspace, Feature.HABITS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.CHORES &&
      isFeatureAvailable(workspace, Feature.CHORES)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.BIG_PLANS &&
      isFeatureAvailable(workspace, Feature.BIG_PLANS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.VACATIONS &&
      isFeatureAvailable(workspace, Feature.VACATIONS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.PROJECTS &&
      isFeatureAvailable(workspace, Feature.PROJECTS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.SMART_LISTS &&
      isFeatureAvailable(workspace, Feature.SMART_LISTS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.METRICS &&
      isFeatureAvailable(workspace, Feature.METRICS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.SLACK_TASKS &&
      isFeatureAvailable(workspace, Feature.SLACK_TASKS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.EMAIL_TASKS &&
      isFeatureAvailable(workspace, Feature.EMAIL_TASKS)
    ) {
      inferredSyncTargets.push(syncTarget);
    }
  }

  return inferredSyncTargets;
}
