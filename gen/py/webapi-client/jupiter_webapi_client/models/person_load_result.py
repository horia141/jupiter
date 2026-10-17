from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_status import AccessStatus
    from ..models.circle import Circle
    from ..models.contact import Contact
    from ..models.inbox_task import InboxTask
    from ..models.location import Location
    from ..models.note import Note
    from ..models.occasion import Occasion
    from ..models.person import Person
    from ..models.person_load_result_occasion_tags_by_ref_id import PersonLoadResultOccasionTagsByRefId
    from ..models.publish_entity import PublishEntity
    from ..models.tag import Tag
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock
    from ..models.user_light import UserLight


T = TypeVar("T", bound="PersonLoadResult")


@_attrs_define
class PersonLoadResult:
    """PersonLoadResult.

    Attributes:
        person (Person): A person.
        contact (Contact): A contact.
        circle_ref_ids (list[str]):
        circles (list[Circle]):
        occasions (list[Occasion]):
        occasion_tags_by_ref_id (PersonLoadResultOccasionTagsByRefId):
        occasion_time_event_blocks (list[TimeEventFullDaysBlock]):
        catch_up_tasks (list[InboxTask]):
        catch_up_tasks_total_cnt (int):
        catch_up_tasks_page_size (int):
        occasion_tasks (list[InboxTask]):
        occasion_tasks_total_cnt (int):
        occasion_tasks_page_size (int):
        tags (list[Tag]):
        owner (UserLight): A user's ref id, name, and email address.
        location (Location | None | Unset):
        note (None | Note | Unset):
        publish_entity (None | PublishEntity | Unset):
        access_status (AccessStatus | None | Unset):
    """

    person: Person
    contact: Contact
    circle_ref_ids: list[str]
    circles: list[Circle]
    occasions: list[Occasion]
    occasion_tags_by_ref_id: PersonLoadResultOccasionTagsByRefId
    occasion_time_event_blocks: list[TimeEventFullDaysBlock]
    catch_up_tasks: list[InboxTask]
    catch_up_tasks_total_cnt: int
    catch_up_tasks_page_size: int
    occasion_tasks: list[InboxTask]
    occasion_tasks_total_cnt: int
    occasion_tasks_page_size: int
    tags: list[Tag]
    owner: UserLight
    location: Location | None | Unset = UNSET
    note: None | Note | Unset = UNSET
    publish_entity: None | PublishEntity | Unset = UNSET
    access_status: AccessStatus | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_status import AccessStatus  # noqa: PLC0415
        from ..models.location import Location  # noqa: PLC0415
        from ..models.note import Note  # noqa: PLC0415
        from ..models.publish_entity import PublishEntity  # noqa: PLC0415

        person = self.person.to_dict()

        contact = self.contact.to_dict()

        circle_ref_ids = self.circle_ref_ids

        circles = []
        for circles_item_data in self.circles:
            circles_item = circles_item_data.to_dict()
            circles.append(circles_item)

        occasions = []
        for occasions_item_data in self.occasions:
            occasions_item = occasions_item_data.to_dict()
            occasions.append(occasions_item)

        occasion_tags_by_ref_id = self.occasion_tags_by_ref_id.to_dict()

        occasion_time_event_blocks = []
        for occasion_time_event_blocks_item_data in self.occasion_time_event_blocks:
            occasion_time_event_blocks_item = occasion_time_event_blocks_item_data.to_dict()
            occasion_time_event_blocks.append(occasion_time_event_blocks_item)

        catch_up_tasks = []
        for catch_up_tasks_item_data in self.catch_up_tasks:
            catch_up_tasks_item = catch_up_tasks_item_data.to_dict()
            catch_up_tasks.append(catch_up_tasks_item)

        catch_up_tasks_total_cnt = self.catch_up_tasks_total_cnt

        catch_up_tasks_page_size = self.catch_up_tasks_page_size

        occasion_tasks = []
        for occasion_tasks_item_data in self.occasion_tasks:
            occasion_tasks_item = occasion_tasks_item_data.to_dict()
            occasion_tasks.append(occasion_tasks_item)

        occasion_tasks_total_cnt = self.occasion_tasks_total_cnt

        occasion_tasks_page_size = self.occasion_tasks_page_size

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        owner = self.owner.to_dict()

        location: dict[str, Any] | None | Unset
        if isinstance(self.location, Unset):
            location = UNSET
        elif isinstance(self.location, Location):
            location = self.location.to_dict()
        else:
            location = self.location

        note: dict[str, Any] | None | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        publish_entity: dict[str, Any] | None | Unset
        if isinstance(self.publish_entity, Unset):
            publish_entity = UNSET
        elif isinstance(self.publish_entity, PublishEntity):
            publish_entity = self.publish_entity.to_dict()
        else:
            publish_entity = self.publish_entity

        access_status: dict[str, Any] | None | Unset
        if isinstance(self.access_status, Unset):
            access_status = UNSET
        elif isinstance(self.access_status, AccessStatus):
            access_status = self.access_status.to_dict()
        else:
            access_status = self.access_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "person": person,
                "contact": contact,
                "circle_ref_ids": circle_ref_ids,
                "circles": circles,
                "occasions": occasions,
                "occasion_tags_by_ref_id": occasion_tags_by_ref_id,
                "occasion_time_event_blocks": occasion_time_event_blocks,
                "catch_up_tasks": catch_up_tasks,
                "catch_up_tasks_total_cnt": catch_up_tasks_total_cnt,
                "catch_up_tasks_page_size": catch_up_tasks_page_size,
                "occasion_tasks": occasion_tasks,
                "occasion_tasks_total_cnt": occasion_tasks_total_cnt,
                "occasion_tasks_page_size": occasion_tasks_page_size,
                "tags": tags,
                "owner": owner,
            }
        )
        if location is not UNSET:
            field_dict["location"] = location
        if note is not UNSET:
            field_dict["note"] = note
        if publish_entity is not UNSET:
            field_dict["publish_entity"] = publish_entity
        if access_status is not UNSET:
            field_dict["access_status"] = access_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_status import AccessStatus  # noqa: PLC0415
        from ..models.circle import Circle  # noqa: PLC0415
        from ..models.contact import Contact  # noqa: PLC0415
        from ..models.inbox_task import InboxTask  # noqa: PLC0415
        from ..models.location import Location  # noqa: PLC0415
        from ..models.note import Note  # noqa: PLC0415
        from ..models.occasion import Occasion  # noqa: PLC0415
        from ..models.person import Person  # noqa: PLC0415
        from ..models.person_load_result_occasion_tags_by_ref_id import PersonLoadResultOccasionTagsByRefId  # noqa: PLC0415
        from ..models.publish_entity import PublishEntity  # noqa: PLC0415
        from ..models.tag import Tag  # noqa: PLC0415
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock  # noqa: PLC0415
        from ..models.user_light import UserLight  # noqa: PLC0415

        d = dict(src_dict)
        person = Person.from_dict(d.pop("person"))

        contact = Contact.from_dict(d.pop("contact"))

        circle_ref_ids = cast(list[str], d.pop("circle_ref_ids"))

        circles = []
        _circles = d.pop("circles")
        for circles_item_data in _circles:
            circles_item = Circle.from_dict(circles_item_data)

            circles.append(circles_item)

        occasions = []
        _occasions = d.pop("occasions")
        for occasions_item_data in _occasions:
            occasions_item = Occasion.from_dict(occasions_item_data)

            occasions.append(occasions_item)

        occasion_tags_by_ref_id = PersonLoadResultOccasionTagsByRefId.from_dict(d.pop("occasion_tags_by_ref_id"))

        occasion_time_event_blocks = []
        _occasion_time_event_blocks = d.pop("occasion_time_event_blocks")
        for occasion_time_event_blocks_item_data in _occasion_time_event_blocks:
            occasion_time_event_blocks_item = TimeEventFullDaysBlock.from_dict(occasion_time_event_blocks_item_data)

            occasion_time_event_blocks.append(occasion_time_event_blocks_item)

        catch_up_tasks = []
        _catch_up_tasks = d.pop("catch_up_tasks")
        for catch_up_tasks_item_data in _catch_up_tasks:
            catch_up_tasks_item = InboxTask.from_dict(catch_up_tasks_item_data)

            catch_up_tasks.append(catch_up_tasks_item)

        catch_up_tasks_total_cnt = d.pop("catch_up_tasks_total_cnt")

        catch_up_tasks_page_size = d.pop("catch_up_tasks_page_size")

        occasion_tasks = []
        _occasion_tasks = d.pop("occasion_tasks")
        for occasion_tasks_item_data in _occasion_tasks:
            occasion_tasks_item = InboxTask.from_dict(occasion_tasks_item_data)

            occasion_tasks.append(occasion_tasks_item)

        occasion_tasks_total_cnt = d.pop("occasion_tasks_total_cnt")

        occasion_tasks_page_size = d.pop("occasion_tasks_page_size")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        owner = UserLight.from_dict(d.pop("owner"))

        def _parse_location(data: object) -> Location | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                location_type_0 = Location.from_dict(data)

                return location_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Location | None | Unset, data)

        location = _parse_location(d.pop("location", UNSET))

        def _parse_note(data: object) -> None | Note | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Note | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_publish_entity(data: object) -> None | PublishEntity | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                publish_entity_type_0 = PublishEntity.from_dict(data)

                return publish_entity_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PublishEntity | Unset, data)

        publish_entity = _parse_publish_entity(d.pop("publish_entity", UNSET))

        def _parse_access_status(data: object) -> AccessStatus | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                access_status_type_0 = AccessStatus.from_dict(data)

                return access_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AccessStatus | None | Unset, data)

        access_status = _parse_access_status(d.pop("access_status", UNSET))

        person_load_result = cls(
            person=person,
            contact=contact,
            circle_ref_ids=circle_ref_ids,
            circles=circles,
            occasions=occasions,
            occasion_tags_by_ref_id=occasion_tags_by_ref_id,
            occasion_time_event_blocks=occasion_time_event_blocks,
            catch_up_tasks=catch_up_tasks,
            catch_up_tasks_total_cnt=catch_up_tasks_total_cnt,
            catch_up_tasks_page_size=catch_up_tasks_page_size,
            occasion_tasks=occasion_tasks,
            occasion_tasks_total_cnt=occasion_tasks_total_cnt,
            occasion_tasks_page_size=occasion_tasks_page_size,
            tags=tags,
            owner=owner,
            location=location,
            note=note,
            publish_entity=publish_entity,
            access_status=access_status,
        )

        person_load_result.additional_properties = d
        return person_load_result

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
