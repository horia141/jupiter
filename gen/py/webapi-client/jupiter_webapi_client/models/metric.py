from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.metric_unit import MetricUnit
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="Metric")


@_attrs_define
class Metric:
    """A metric.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): THe metric name.
        metric_collection_ref_id (str):
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        icon (Union[None, Unset, str]):
        collection_params (Union['RecurringTaskGenParams', None, Unset]):
        metric_unit (Union[MetricUnit, None, Unset]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    metric_collection_ref_id: str
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    icon: Union[None, Unset, str] = UNSET
    collection_params: Union["RecurringTaskGenParams", None, Unset] = UNSET
    metric_unit: Union[MetricUnit, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        metric_collection_ref_id = self.metric_collection_ref_id

        archival_reason: Union[None, Unset, str]
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        icon: Union[None, Unset, str]
        if isinstance(self.icon, Unset):
            icon = UNSET
        else:
            icon = self.icon

        collection_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.collection_params, Unset):
            collection_params = UNSET
        elif isinstance(self.collection_params, RecurringTaskGenParams):
            collection_params = self.collection_params.to_dict()
        else:
            collection_params = self.collection_params

        metric_unit: Union[None, Unset, str]
        if isinstance(self.metric_unit, Unset):
            metric_unit = UNSET
        elif isinstance(self.metric_unit, MetricUnit):
            metric_unit = self.metric_unit.value
        else:
            metric_unit = self.metric_unit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "metric_collection_ref_id": metric_collection_ref_id,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if icon is not UNSET:
            field_dict["icon"] = icon
        if collection_params is not UNSET:
            field_dict["collection_params"] = collection_params
        if metric_unit is not UNSET:
            field_dict["metric_unit"] = metric_unit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        metric_collection_ref_id = d.pop("metric_collection_ref_id")

        def _parse_archival_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_icon(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        icon = _parse_icon(d.pop("icon", UNSET))

        def _parse_collection_params(data: object) -> Union["RecurringTaskGenParams", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                collection_params_type_0 = RecurringTaskGenParams.from_dict(data)

                return collection_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RecurringTaskGenParams", None, Unset], data)

        collection_params = _parse_collection_params(d.pop("collection_params", UNSET))

        def _parse_metric_unit(data: object) -> Union[MetricUnit, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                metric_unit_type_0 = MetricUnit(data)

                return metric_unit_type_0
            except:  # noqa: E722
                pass
            return cast(Union[MetricUnit, None, Unset], data)

        metric_unit = _parse_metric_unit(d.pop("metric_unit", UNSET))

        metric = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            metric_collection_ref_id=metric_collection_ref_id,
            archival_reason=archival_reason,
            archived_time=archived_time,
            icon=icon,
            collection_params=collection_params,
            metric_unit=metric_unit,
        )

        metric.additional_properties = d
        return metric

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
