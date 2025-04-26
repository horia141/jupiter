import {
  type User,
  type Workspace,
  SyncTarget,
  WorkspaceFeature,
  UserFeature,
} from "@jupiter/webapi-client";

import { isUserFeatureAvailable } from "./user";
import { isWorkspaceFeatureAvailable } from "./workspace";

export function inferSyncTargetsForEnabledFeatures(
  user: User,
  workspace: Workspace,
  syncTargets: Array<SyncTarget>,
): Array<SyncTarget> {
  // Keep in sync with python:core:infer_sync_targets_for_enabled_features
  const inferredSyncTargets: Array<SyncTarget> = [];

  for (const syncTarget of syncTargets) {
    if (
      syncTarget === SyncTarget.INBOX_TASKS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.INBOX_TASKS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.WORKING_MEM &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.WORKING_MEM)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.TIME_PLANS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.SCHEDULE &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.HABITS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.HABITS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.CHORES &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.CHORES)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.BIG_PLANS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.BIG_PLANS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.JOURNALS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.JOURNALS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.DOCS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.DOCS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.VACATIONS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.VACATIONS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.PROJECTS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PROJECTS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.PERSONS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PERSONS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.SMART_LISTS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SMART_LISTS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.METRICS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.METRICS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.SLACK_TASKS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SLACK_TASKS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.EMAIL_TASKS &&
      isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.EMAIL_TASKS)
    ) {
      inferredSyncTargets.push(syncTarget);
    } else if (
      syncTarget === SyncTarget.GAMIFICATION &&
      isUserFeatureAvailable(user, UserFeature.GAMIFICATION)
    ) {
      inferredSyncTargets.push(syncTarget);
    }
  }

  return inferredSyncTargets;
}
