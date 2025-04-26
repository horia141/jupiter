from collections.abc import Iterable

from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.sync_target import SyncTarget


def infer_sync_targets_for_enabled_features(
    user: User, workspace: Workspace, sync_targets: Iterable[SyncTarget] | None = None
) -> list[SyncTarget]:
    """Filter and complete a set of sources according to the enabled features."""
    # Keep in sync with ts:webui:inferSyncTargetsForEnabledFeatures
    all_sync_targets = sync_targets or [s for s in SyncTarget]
    inferred_sync_targets: list[SyncTarget] = []
    for sync_target in all_sync_targets:
        if sync_target is SyncTarget.INBOX_TASKS and workspace.is_feature_available(
            WorkspaceFeature.INBOX_TASKS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.WORKING_MEM and workspace.is_feature_available(
            WorkspaceFeature.WORKING_MEM
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.TIME_PLANS and workspace.is_feature_available(
            WorkspaceFeature.TIME_PLANS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.SCHEDULES and workspace.is_feature_available(
            WorkspaceFeature.SCHEDULE
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.HABITS and workspace.is_feature_available(
            WorkspaceFeature.HABITS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.CHORES and workspace.is_feature_available(
            WorkspaceFeature.CHORES
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.BIG_PLANS and workspace.is_feature_available(
            WorkspaceFeature.BIG_PLANS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.JOURNALS and workspace.is_feature_available(
            WorkspaceFeature.JOURNALS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.DOCS and workspace.is_feature_available(
            WorkspaceFeature.DOCS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.VACATIONS and workspace.is_feature_available(
            WorkspaceFeature.VACATIONS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.PROJECTS and workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.PERSONS and workspace.is_feature_available(
            WorkspaceFeature.PERSONS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.SMART_LISTS and workspace.is_feature_available(
            WorkspaceFeature.SMART_LISTS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.METRICS and workspace.is_feature_available(
            WorkspaceFeature.METRICS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.PERSONS and workspace.is_feature_available(
            WorkspaceFeature.PERSONS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.SLACK_TASKS and workspace.is_feature_available(
            WorkspaceFeature.SLACK_TASKS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.EMAIL_TASKS and workspace.is_feature_available(
            WorkspaceFeature.EMAIL_TASKS
        ):
            inferred_sync_targets.append(sync_target)
        elif sync_target is SyncTarget.GAMIFICATION and user.is_feature_available(
            UserFeature.GAMIFICATION
        ):
            inferred_sync_targets.append(sync_target)
    return inferred_sync_targets
