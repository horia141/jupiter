from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

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
        metric_collection (str):
        archived_time (Union[Unset, str]): A timestamp in the application.
        icon (Union[Unset, str]): The icon for an entity.
        collection_params (Union[Unset, RecurringTaskGenParams]): Parameters for metric collection.
        metric_unit (Union[Unset, MetricUnit]): The unit for a metric.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    metric_collection: str
    archived_time: Union[Unset, str] = UNSET
    icon: Union[Unset, str] = UNSET
    collection_params: Union[Unset, "RecurringTaskGenParams"] = UNSET
    metric_unit: Union[Unset, MetricUnit] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        metric_collection = self.metric_collection

        archived_time = self.archived_time

        icon = self.icon

        collection_params: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.collection_params, Unset):
            collection_params = self.collection_params.to_dict()

        metric_unit: Union[Unset, str] = UNSET
        if not isinstance(self.metric_unit, Unset):
            metric_unit = self.metric_unit.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "metric_collection": metric_collection,
            }
        )
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        metric_collection = d.pop("metric_collection")

        archived_time = d.pop("archived_time", UNSET)

        icon = d.pop("icon", UNSET)

        _collection_params = d.pop("collection_params", UNSET)
        collection_params: Union[Unset, RecurringTaskGenParams]
        if isinstance(_collection_params, Unset):
            collection_params = UNSET
        else:
            collection_params = RecurringTaskGenParams.from_dict(_collection_params)

        _metric_unit = d.pop("metric_unit", UNSET)
        metric_unit: Union[Unset, MetricUnit]
        if isinstance(_metric_unit, Unset):
            metric_unit = UNSET
        else:
            metric_unit = MetricUnit(_metric_unit)

        metric = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            metric_collection=metric_collection,
            archived_time=archived_time,
            icon=icon,
            collection_params=collection_params,
            metric_unit=metric_unit,
        )

        metric.additional_properties = d
        return metric

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
