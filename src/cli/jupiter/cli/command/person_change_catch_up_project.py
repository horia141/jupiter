"""UseCase for updating the person database."""
from argparse import ArgumentParser, Namespace
from typing import Optional

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.persons.change_catch_up_project import (
    PersonChangeCatchUpProjectArgs,
    PersonChangeCatchUpProjectUseCase,
)


class PersonChangeCatchUpProject(
    LoggedInMutationCommand[PersonChangeCatchUpProjectUseCase]
):
    """UseCase for updating the person database."""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        catch_up_project_group = parser.add_mutually_exclusive_group()
        catch_up_project_group.add_argument(
            "--catch-up-project",
            dest="catch_up_project_ref_id",
            required=False,
            help="The project key to generate recurring catch up tasks",
        )
        catch_up_project_group.add_argument(
            "--clear-catch-up-project",
            dest="clear_catch_up_project",
            required=False,
            default=False,
            action="store_const",
            const=True,
            help="Clear the catch up project",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        catch_up_project_ref_id: Optional[EntityId]
        if args.clear_catch_up_project:
            catch_up_project_ref_id = None
        else:
            catch_up_project_ref_id = EntityId.from_raw(args.catch_up_project_ref_id)

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            PersonChangeCatchUpProjectArgs(
                catch_up_project_ref_id=catch_up_project_ref_id
            ),
        )
