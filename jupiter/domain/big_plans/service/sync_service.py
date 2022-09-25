"""The service class for dealing with big plans."""
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class BigPlanSyncService(
    TrunkLeafNotionSyncService[
        BigPlanCollection,
        BigPlan,
        NotionWorkspace,
        NotionBigPlanCollection,
        NotionBigPlan,
        NotionBigPlan.DirectInfo,
        NotionBigPlan.InverseInfo,
    ]
):
    """The service class for dealing with big plans."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        big_plan_notion_manager: BigPlanNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            BigPlanCollection,
            BigPlan,
            "big plan",
            NotionBigPlan,
            storage_engine,
            big_plan_notion_manager,
        )
