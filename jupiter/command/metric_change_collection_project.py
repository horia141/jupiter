"""UseCase for updating the metric collection project."""
from argparse import ArgumentParser, Namespace
from typing import Final, Optional

from jupiter.command.command import Command
from jupiter.command.rendering import RichConsoleProgressReporter
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.use_cases.metrics.change_collection_project import (
    MetricChangeCollectionProjectUseCase,
)


class MetricChangeCollectionProject(Command):
    """Use case for updating the metric collection project."""

    _command: Final[MetricChangeCollectionProjectUseCase]

    def __init__(self, the_command: MetricChangeCollectionProjectUseCase):
        """Constructor."""
        self._command = the_command

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "metric-change-collection-project"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the collection project for metrics"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        collection_project_group = parser.add_mutually_exclusive_group()
        collection_project_group.add_argument(
            "--collection-project",
            dest="collection_project_key",
            required=False,
            help="The project key to generate collection tasks",
        )
        collection_project_group.add_argument(
            "--clear-collection-project",
            dest="clear_collection_project_key",
            required=False,
            default=False,
            action="store_const",
            const=True,
            help="Clear the collection project",
        )

    def run(
        self, progress_reporter: RichConsoleProgressReporter, args: Namespace
    ) -> None:
        """Callback to execute when the command is invoked."""
        collection_project_key: Optional[ProjectKey]
        if args.clear_collection_project_key:
            collection_project_key = None
        else:
            collection_project_key = ProjectKey.from_raw(args.collection_project_key)

        self._command.execute(
            progress_reporter,
            MetricChangeCollectionProjectUseCase.Args(
                collection_project_key=collection_project_key
            ),
        )
