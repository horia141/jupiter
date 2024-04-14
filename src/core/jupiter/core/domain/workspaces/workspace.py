"""The workspace where everything happens."""
import abc
from collections.abc import Iterable

from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.features import (
    WorkspaceFeature,
    WorkspaceFeatureFlags,
    WorkspaceFeatureFlagsControls,
)
from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.journals.journal_collection import JournalCollection
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import BAD_REF_ID
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsOne,
    IsRefId,
    RootEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import EntityNotFoundError, RootEntityRepository
from jupiter.core.framework.update_action import UpdateAction


@entity
class Workspace(RootEntity):
    """The workspace where everything happens."""

    name: WorkspaceName
    feature_flags: WorkspaceFeatureFlags

    inbox_task_collection = ContainsOne(InboxTaskCollection, workspace_ref_id=IsRefId())
    habit_collection = ContainsOne(HabitCollection, workspace_ref_id=IsRefId())
    chore_collection = ContainsOne(ChoreCollection, workspace_ref_id=IsRefId())
    big_plan_collection = ContainsOne(BigPlanCollection, workspace_ref_id=IsRefId())
    journal_collection = ContainsOne(JournalCollection, workspace_ref_id=IsRefId())
    doc_collection = ContainsOne(DocCollection, workspace_ref_id=IsRefId())
    vacation_collection = ContainsOne(VacationCollection, workspace_ref_id=IsRefId())
    project_collection = ContainsOne(ProjectCollection, workspace_ref_id=IsRefId())
    smart_list_collection = ContainsOne(SmartListCollection, workspace_ref_id=IsRefId())
    metric_collection = ContainsOne(MetricCollection, workspace_ref_id=IsRefId())
    person_collection = ContainsOne(PersonCollection, workspace_ref_id=IsRefId())
    push_integration_group = ContainsOne(
        PushIntegrationGroup, workspace_ref_id=IsRefId()
    )

    note_collection = ContainsOne(NoteCollection, workspace_ref_id=IsRefId())

    gc_log = ContainsOne(GCLog, workspace_ref_id=IsRefId())
    gen_log = ContainsOne(GenLog, workspace_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_workspace(
        ctx: DomainContext,
        name: WorkspaceName,
        feature_flag_controls: WorkspaceFeatureFlagsControls,
        feature_flags: WorkspaceFeatureFlags,
    ) -> "Workspace":
        """Create a new workspace."""
        return Workspace._create(
            ctx,
            name=name,
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta=feature_flags, current_feature_flags={}
            ),
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[WorkspaceName],
    ) -> "Workspace":
        """Update properties of the workspace."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
        )

    @update_entity_action
    def change_feature_flags(
        self,
        ctx: DomainContext,
        feature_flag_controls: WorkspaceFeatureFlagsControls,
        feature_flags: WorkspaceFeatureFlags,
    ) -> "Workspace":
        """Change the feature settings for this workspace."""
        return self._new_version(
            ctx,
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta=feature_flags,
                current_feature_flags=self.feature_flags,
            ),
        )

    def is_feature_available(self, feature: WorkspaceFeature) -> bool:
        """Check if a feature is available in this workspace."""
        return self.feature_flags[feature]

    def infer_entity_tags_for_enabled_features(
        self, filter_entity_tags: Iterable[NamedEntityTag] | None = None
    ) -> list[NamedEntityTag]:
        """Filter and complete a set of entity tags according to the enabled features."""
        # Keep in sync with ts:webui:interEntityTagsForEnabledFeatures
        all_entity_tags = filter_entity_tags or [s for s in NamedEntityTag]
        inferred_entity_tags: list[NamedEntityTag] = []
        for entity_tag in all_entity_tags:
            if entity_tag is NamedEntityTag.INBOX_TASK:
                inferred_entity_tags.append(entity_tag)
            elif entity_tag is NamedEntityTag.WORKING_MEM and self.is_feature_available(
                WorkspaceFeature.WORKING_MEM
            ):
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
            elif entity_tag is NamedEntityTag.JOURNAL and self.is_feature_available(
                WorkspaceFeature.JOURNALS
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
    ) -> list[InboxTaskSource]:
        """Filter and complete a set of sources according to the enabled features."""
        # Keep in sync with ts:webui:inferSourcesForEnabledFeatures
        all_sources = filter_sources or [s for s in InboxTaskSource]
        inferred_sources: list[InboxTaskSource] = []
        for source in all_sources:
            if source is InboxTaskSource.USER:
                inferred_sources.append(source)
            elif (
                source is InboxTaskSource.WORKING_MEM_CLEANUP
                and self.is_feature_available(WorkspaceFeature.WORKING_MEM)
            ):
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
            elif source is InboxTaskSource.JOURNAL and self.is_feature_available(
                WorkspaceFeature.JOURNALS
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
    ) -> list[SyncTarget]:
        """Filter and complete a set of sources according to the enabled features."""
        # Keep in sync with ts:webui:inferSyncTargetsForEnabledFeatures
        all_sync_targets = sync_targets or [s for s in SyncTarget]
        inferred_sync_targets: list[SyncTarget] = []
        for sync_target in all_sync_targets:
            if sync_target is SyncTarget.INBOX_TASKS and self.is_feature_available(
                WorkspaceFeature.INBOX_TASKS
            ):
                inferred_sync_targets.append(sync_target)
            elif sync_target is SyncTarget.WORKING_MEM and self.is_feature_available(
                WorkspaceFeature.WORKING_MEM
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
            elif sync_target is SyncTarget.JOURNALS and self.is_feature_available(
                WorkspaceFeature.JOURNALS
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


class WorkspaceNotFoundError(EntityNotFoundError):
    """Error raised when a workspace is not found."""


class WorkspaceRepository(RootEntityRepository[Workspace], abc.ABC):
    """A repository for workspaces."""
