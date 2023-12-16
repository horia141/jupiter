"""Archive a doc."""
from typing import Final

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class DocArchiveService:
    """A service for removing a doc."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider

    async def do_it(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        doc: Doc,
    ) -> None:
        """Execute the command's action."""
        if doc.archived:
            return

        subdocs = await uow.doc_repository.find_all_with_filters(
            parent_ref_id=doc.doc_collection_ref_id,
            allow_archived=True,
            filter_parent_doc_ref_ids=[doc.ref_id],
        )

        for subdoc in subdocs:
            await self.do_it(uow, progress_reporter, subdoc)

        note_archive_service = NoteArchiveService(self._source, self._time_provider)
        await note_archive_service.archive_for_source(uow, NoteDomain.DOC, doc.ref_id)

        doc = doc.mark_archived(self._source, self._time_provider.get_current_time())
        await uow.doc_repository.save(doc)
        await progress_reporter.mark_updated(doc)
