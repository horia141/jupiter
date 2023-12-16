"""The workspace where everything happens."""
from dataclasses import dataclass
from typing import Iterable, List

from jupiter.core.domain.features import (
    WorkspaceFeature,
    WorkspaceFeatureFlags,
    WorkspaceFeatureFlagsControls,
)
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.named_entity_tag import NamedEntityTag
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
    feature_flags: WorkspaceFeatureFlags

    @staticmethod
    def new_workspace(
        name: WorkspaceName,
        feature_flag_controls: WorkspaceFeatureFlagsControls,
        feature_flags: WorkspaceFeatureFlags,
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
            feature_flags=feature_flag_controls.validate_and_complete(
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
        feature_flag_controls: WorkspaceFeatureFlagsControls,
        feature_flags: WorkspaceFeatureFlags,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Workspace":
        """Change the feature settings for this workspace."""
        return self._new_version(
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta=feature_flags,
                current_feature_flags=self.feature_flags,
            ),
            new_event=Workspace.UpdateFeatureFlags.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    def is_feature_available(self, feature: WorkspaceFeature) -> bool:
        """Check if a feature is available in this workspace."""
        return self.feature_flags[feature]

    def infer_entity_tags_for_enabled_features(
        self, filter_entity_tags: Iterable[NamedEntityTag] | None = None
    ) -> List[NamedEntityTag]:
        """Filter and complete a set of entity tags according to the enabled features."""
        # Keep in sync with ts:webui:interEntityTagsForEnabledFeatures
        all_entity_tags = filter_entity_tags or [s for s in NamedEntityTag]
        inferred_entity_tags: List[NamedEntityTag] = []
        for entity_tag in all_entity_tags:
            if entity_tag is NamedEntityTag.INBOX_TASK:
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.HABIT and self.is_feature_available(
                WorkspaceFeature.HABITS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.CHORE and self.is_feature_available(
                WorkspaceFeature.CHORES
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.BIG_PLAN and self.is_feature_available(
                WorkspaceFeature.BIG_PLANS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.DOC and self.is_feature_available(
                WorkspaceFeature.DOCS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.VACATION and self.is_feature_available(
                WorkspaceFeature.VACATIONS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.PROJECT and self.is_feature_available(
                WorkspaceFeature.PROJECTS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.SMART_LIST and self.is_feature_available(
                WorkspaceFeature.SMART_LISTS
            ):
                inferred_entity_tags.append(entity_tag)
            elif (
                entity_tag is NamedEntityTag.SMART_LIST_TAG
                and self.is_feature_available(WorkspaceFeature.SMART_LISTS)
            ):
                inferred_entity_tags.append(entity_tag)
            elif (
                entity_tag is NamedEntityTag.SMART_LIST_ITEM
                and self.is_feature_available(WorkspaceFeature.SMART_LISTS)
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.METRIC and self.is_feature_available(
                WorkspaceFeature.METRICS
            ):
                inferred_entity_tags.append(entity_tag)
            elif (
                entity_tag is NamedEntityTag.METRIC_ENTRY
                and self.is_feature_available(WorkspaceFeature.METRICS)
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.PERSON and self.is_feature_available(
                WorkspaceFeature.PERSONS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.SLACK_TASK and self.is_feature_available(
                WorkspaceFeature.SLACK_TASKS
            ):
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.EMAIL_TASK and self.is_feature_available(
                WorkspaceFeature.EMAIL_TASKS
            ):
                inferred_entity_tags.append(entity_tag)
        return inferred_entity_tags

    def infer_sources_for_enabled_features(
        self, filter_sources: Iterable[InboxTaskSource] | None = None
    ) -> List[InboxTaskSource]:
        """Filter and complete a set of sources according to the enabled features."""
        # Keep in sync with ts:webui:inferSourcesForEnabledFeatures
        all_sources = filter_sources or [s for s in InboxTaskSource]
        inferred_sources: List[InboxTaskSource] = []
        for source in all_sources:
            if source is InboxTaskSource.USER:
                inferred_sources.append(source)
            elif source is InboxTaskSource.HABIT and self.is_feature_available(
                WorkspaceFeature.HABITS
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.CHORE and self.is_feature_available(
                WorkspaceFeature.CHORES
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.BIG_PLAN and self.is_feature_available(
                WorkspaceFeature.BIG_PLANS
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.METRIC and self.is_feature_available(
                WorkspaceFeature.METRICS
            ):
                inferred_sources.append(source)
            elif (
                source is InboxTaskSource.PERSON_BIRTHDAY
                and self.is_feature_available(WorkspaceFeature.PERSONS)
            ):
                inferred_sources.append(source)
            elif (
                source is InboxTaskSource.PERSON_CATCH_UP
                and self.is_feature_available(WorkspaceFeature.PERSONS)
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.SLACK_TASK and self.is_feature_available(
                WorkspaceFeature.SLACK_TASKS
            ):
                inferred_sources.append(source)
            elif source is InboxTaskSource.EMAIL_TASK and self.is_feature_available(
                WorkspaceFeature.EMAIL_TASKS
            ):
                inferred_sources.append(source)
        return inferred_sources

    def infer_sync_targets_for_enabled_features(
        self, sync_targets: Iterable[SyncTarget] | None = None
    ) -> List[SyncTarget]:
        """Filter and complete a set of sources according to the enabled features."""
        # Keep in sync with ts:webui:inferSyncTargetsForEnabledFeatures
        all_sync_targets = sync_targets or [s for s in SyncTarget]
        inferred_sync_targets: List[SyncTarget] = []
        for sync_target in all_sync_targets:
            if sync_target is SyncTarget.INBOX_TASKS and self.is_feature_available(
                WorkspaceFeature.INBOX_TASKS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.HABITS and self.is_feature_available(
                WorkspaceFeature.HABITS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.CHORES and self.is_feature_available(
                WorkspaceFeature.CHORES
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.BIG_PLANS and self.is_feature_available(
                WorkspaceFeature.BIG_PLANS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.DOCS and self.is_feature_available(
                WorkspaceFeature.DOCS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.VACATIONS and self.is_feature_available(
                WorkspaceFeature.VACATIONS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.PROJECTS and self.is_feature_available(
                WorkspaceFeature.PROJECTS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.SMART_LISTS and self.is_feature_available(
                WorkspaceFeature.SMART_LISTS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.METRICS and self.is_feature_available(
                WorkspaceFeature.METRICS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.PERSONS and self.is_feature_available(
                WorkspaceFeature.PERSONS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.SLACK_TASKS and self.is_feature_available(
                WorkspaceFeature.SLACK_TASKS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.EMAIL_TASKS and self.is_feature_available(
                WorkspaceFeature.EMAIL_TASKS
            ):
                inferred_sync_targets.append(sync_target)
        return inferred_sync_targets
