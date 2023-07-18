"""The workspace where everything happens."""
from dataclasses import dataclass
from typing import Iterable, List

from jupiter.core.domain.features import (
    Feature,
    FeatureFlags,
    FeatureFlagsControls,
)
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, RootEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Workspace(RootEntity):
    """The workspace where everything happens."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    @dataclass
    class ChangedDefaultProject(Entity.Updated):
        """Changed the default project."""

    @dataclass
    class UpdateFeatureFlags(Entity.Updated):
        """Changed the feature flags for the workspace."""

    name: WorkspaceName
    default_project_ref_id: EntityId
    feature_flags: FeatureFlags

    @staticmethod
    def new_workspace(
        name: WorkspaceName,
        feature_flag_controls: FeatureFlagsControls,
        feature_flags: FeatureFlags,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Workspace":
        """Create a new workspace."""
        workspace = Workspace(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Workspace.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=name,
            feature_flags=feature_flag_controls.validate_and_complete_feature_flags(
                feature_flags_delta=feature_flags, current_feature_flags={}
            ),
            default_project_ref_id=BAD_REF_ID,
        )
        return workspace

    def update(
        self,
        name: UpdateAction[WorkspaceName],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Workspace":
        """Update properties of the workspace."""
        return self._new_version(
            name=name.or_else(self.name),
            new_event=Workspace.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def change_default_project(
        self,
        default_project_ref_id: EntityId,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Workspace":
        """Change the default project of the workspace."""
        return self._new_version(
            default_project_ref_id=default_project_ref_id,
            new_event=Workspace.ChangedDefaultProject.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def change_feature_flags(
        self,
        feature_flag_controls: FeatureFlagsControls,
        feature_flags: FeatureFlags,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Workspace":
        """Change the feature settings for this workspace."""
        return self._new_version(
            feature_flags=feature_flag_controls.validate_and_complete_feature_flags(
                feature_flags_delta=feature_flags,
                current_feature_flags=self.feature_flags,
            ),
            new_event=Workspace.UpdateFeatureFlags.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    def is_feature_available(self, feature: Feature) -> bool:
        """Check if a feature is available in this workspace."""
        return self.feature_flags[feature]

    def infer_sources_for_enabled_features(
        self, filter_sources: Iterable[InboxTaskSource] | None = None
    ) -> List[InboxTaskSource]:
        """Filter and complete a set of sources according to the enabled features."""
        all_sources = filter_sources or [s for s in InboxTaskSource]
        inferred_sources: List[InboxTaskSource] = []
        for source in all_sources:
            if source is InboxTaskSource.USER:
                inferred_sources.append(source)
            elif source is InboxTaskSource.HABIT and self.is_feature_available(
                Feature.HABITS
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.CHORE and self.is_feature_available(
                Feature.CHORES
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.BIG_PLAN and self.is_feature_available(
                Feature.BIG_PLANS
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.METRIC and self.is_feature_available(
                Feature.METRICS
            ):
                inferred_sources.append(source)
            elif (
                source is InboxTaskSource.PERSON_BIRTHDAY
                and self.is_feature_available(Feature.PERSONS)
            ):
                inferred_sources.append(source)
            elif (
                source is InboxTaskSource.PERSON_CATCH_UP
                and self.is_feature_available(Feature.PERSONS)
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.SLACK_TASK and self.is_feature_available(
                Feature.SLACK_TASKS
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.EMAIL_TASK and self.is_feature_available(
                Feature.EMAIL_TASKS
            ):
                inferred_sources.append(source)
        return inferred_sources

    def infer_sync_targets_for_enabled_features(
        self, sync_targets: Iterable[SyncTarget] | None = None
    ) -> List[SyncTarget]:
        """Filter and complete a set of sources according to the enabled features."""
        all_sources = sync_targets or [s for s in SyncTarget]
        inferred_sources: List[SyncTarget] = []
        for sync_target in all_sources:
            if sync_target is SyncTarget.INBOX_TASKS and self.is_feature_available(
                Feature.INBOX_TASKS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.HABITS and self.is_feature_available(
                Feature.HABITS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.CHORES and self.is_feature_available(
                Feature.CHORES
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.BIG_PLANS and self.is_feature_available(
                Feature.BIG_PLANS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.VACATIONS and self.is_feature_available(
                Feature.VACATIONS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.PROJECTS and self.is_feature_available(
                Feature.PROJECTS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.SMART_LISTS and self.is_feature_available(
                Feature.SMART_LISTS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.METRICS and self.is_feature_available(
                Feature.METRICS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.PERSONS and self.is_feature_available(
                Feature.PERSONS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.SLACK_TASKS and self.is_feature_available(
                Feature.SLACK_TASKS
            ):
                inferred_sources.append(sync_target)
            elif sync_target is SyncTarget.EMAIL_TASKS and self.is_feature_available(
                Feature.EMAIL_TASKS
            ):
                inferred_sources.append(sync_target)
        return inferred_sources
