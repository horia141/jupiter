import { Feature, InboxTaskSource, SyncTarget, Workspace } from "jupiter-gen";

export function isFeatureAvailable(
  workspace: Workspace,
  feature: Feature
): boolean {
  return workspace.feature_flags[feature];
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
