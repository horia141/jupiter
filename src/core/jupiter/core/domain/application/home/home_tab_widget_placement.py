"""Placement of widgets on a tab."""

import abc
from typing import Literal

from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.value import CompositeValue, value


@value
class HomeTabWidgetPlacement(CompositeValue, abc.ABC):
    """The placement of widgets on a tab."""


@value
class BigScreenHomeTabWidgetPlacement(HomeTabWidgetPlacement):
    """The placement of widgets on a tab for big screen."""

    kind: Literal["big-screen"]
    rows: list[list[EntityId]]

    @staticmethod
    def empty() -> "BigScreenHomeTabWidgetPlacement":
        return BigScreenHomeTabWidgetPlacement(kind="big-screen", rows=[])


@value
class SmallScreenHomeTabWidgetPlacement(HomeTabWidgetPlacement):
    """The placement of widgets on a tab for small screen."""

    kind: Literal["small-screen"]
    rows: list[EntityId]

    @staticmethod
    def empty() -> "SmallScreenHomeTabWidgetPlacement":
        return SmallScreenHomeTabWidgetPlacement(kind="small-screen", rows=[])

OneOfHomeTabWidgetPlacement = BigScreenHomeTabWidgetPlacement | SmallScreenHomeTabWidgetPlacement

def build_home_tab_widget_placement(
    target: HomeTabTarget,
) -> OneOfHomeTabWidgetPlacement:
    if target == HomeTabTarget.BIG_SCREEN:
        return BigScreenHomeTabWidgetPlacement.empty()
    else:
        return SmallScreenHomeTabWidgetPlacement.empty()
