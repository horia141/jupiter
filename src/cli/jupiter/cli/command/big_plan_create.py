"""UseCase for creating big plans."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.core.framework.realm import RealmCodecRegistry

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.big_plans.create import (
    BigPlanCreateArgs,
    BigPlanCreateUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties


class BigPlanCreate(LoggedInMutationCommand[BigPlanCreateUseCase]):
    """UseCase class for creating big plans."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        global_properties: GlobalProperties,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: BigPlanCreateUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(
                    realm_codec_registry,session_storage, top_level_context, use_case)
        self._global_properties = global_properties
