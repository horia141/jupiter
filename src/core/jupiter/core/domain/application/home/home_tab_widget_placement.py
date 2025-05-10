"""Placement of widgets on a tab."""

import abc
from typing import Literal

from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.domain.application.home.widget import WidgetDimension, WidgetGeometry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import CompositeValue, value

@value
class HomeTabWidgetPlacementSection(CompositeValue):
    """A section of the placement of widgets on a tab."""

    ref_id: EntityId
    geometry: WidgetGeometry


@value
class HomeTabWidgetPlacement(CompositeValue, abc.ABC):
    """The placement of widgets on a tab."""

    @abc.abstractmethod
    def add_widget(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "HomeTabWidgetPlacement":
        pass

    @abc.abstractmethod
    def remove_widget(
        self,
        widget_ref_id: EntityId,
    ) -> "HomeTabWidgetPlacement":
        pass

    @abc.abstractmethod
    def move_widget_to(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "HomeTabWidgetPlacement":
        pass
    


@value
class BigScreenHomeTabWidgetPlacement(HomeTabWidgetPlacement):
    """The placement of widgets on a tab for big screen."""

    kind: Literal["big-screen"]
    rows: list[list[EntityId]]

    @staticmethod
    def empty() -> "BigScreenHomeTabWidgetPlacement":
        return BigScreenHomeTabWidgetPlacement(kind="big-screen", rows=[])
    
    def add_widget(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "BigScreenHomeTabWidgetPlacement":
        pass

    def remove_widget(
        self,
        widget_ref_id: EntityId,
    ) -> "BigScreenHomeTabWidgetPlacement":
        pass

    def move_widget_to(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "BigScreenHomeTabWidgetPlacement":
        pass



@value
class SmallScreenHomeTabWidgetPlacement(HomeTabWidgetPlacement):
    """The placement of widgets on a tab for small screen."""

    _ALLOWED_DIMENSIONS = [WidgetDimension.DIM_1x1, WidgetDimension.DIM_2x1, WidgetDimension.DIM_3x1, WidgetDimension.DIM_kx1]

    kind: Literal["small-screen"]
    sections: list[HomeTabWidgetPlacementSection]

    @staticmethod
    def empty() -> "SmallScreenHomeTabWidgetPlacement":
        return SmallScreenHomeTabWidgetPlacement(kind="small-screen", sections=[])
    
    def add_widget(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "SmallScreenHomeTabWidgetPlacement":
        """Add a widget to the placement."""
        if geometry.col != 0:
            raise InputValidationError("Column must be 0")
        if geometry.dimension not in SmallScreenHomeTabWidgetPlacement._ALLOWED_DIMENSIONS:
            raise InputValidationError(f"Dimension {geometry.dimension} is not allowed for small screen")
        if geometry.row < len(self.sections):
            # kx1 can only be last element
            if geometry.dimension == WidgetDimension.DIM_kx1:
                raise InputValidationError("kx1 dimension can only be used as the last element")
            
            # Check no kx1 elements before this position
            for i in range(geometry.row):
                if self.sections[i].geometry.dimension == WidgetDimension.DIM_kx1:
                    raise InputValidationError("Cannot insert after kx1 element")
                    
            # Insert at position by shifting everything right
            new_sections = (
                self.sections[:geometry.row] + 
                [HomeTabWidgetPlacementSection(widget_ref_id, geometry)] +
                self.sections[geometry.row:]
            )
            return SmallScreenHomeTabWidgetPlacement(kind=self.kind, sections=new_sections)
            
        elif geometry.row == len(self.sections):
            # Check no kx1 elements before this position
            for section in self.sections:
                if section.geometry.dimension == WidgetDimension.DIM_kx1:
                    raise InputValidationError("Cannot add after kx1 element")
                    
            # Append as last element
            return SmallScreenHomeTabWidgetPlacement(
                kind=self.kind,
                sections=self.sections + [HomeTabWidgetPlacementSection(widget_ref_id, geometry)]
            )
            
        else:
            raise InputValidationError(f"Row {geometry.row} is not valid")

    def remove_widget(
        self,
        widget_ref_id: EntityId,
    ) -> "SmallScreenHomeTabWidgetPlacement":
        """Remove a widget from the placement."""
        new_sections = [section for section in self.sections if section.ref_id != widget_ref_id]
        return SmallScreenHomeTabWidgetPlacement(kind=self.kind, sections=new_sections)

    def move_widget_to(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "SmallScreenHomeTabWidgetPlacement":
        """Move a widget to a new position."""
        if geometry.col != 0:
            raise InputValidationError("Column must be 0")
        if geometry.dimension not in SmallScreenHomeTabWidgetPlacement._ALLOWED_DIMENSIONS:
            raise InputValidationError(f"Dimension {geometry.dimension} is not allowed for small screen")
        widget_in_place = next((section for section in self.sections if section.ref_id == widget_ref_id), None)
        if widget_in_place is None:
            raise InputValidationError(f"Widget {widget_ref_id} not found")
        if widget_in_place.geometry.dimension == WidgetDimension.DIM_kx1:
            raise InputValidationError("kx1 dimension cannot be moved")
        new_thing = self.remove_widget(widget_ref_id)
        if geometry.row > widget_in_place.geometry.row:
            geometry = geometry.with_row(geometry.row - 1)
        return new_thing.add_widget(widget_ref_id, geometry)
    

OneOfHomeTabWidgetPlacement = BigScreenHomeTabWidgetPlacement | SmallScreenHomeTabWidgetPlacement

def build_home_tab_widget_placement(
    target: HomeTabTarget,
) -> OneOfHomeTabWidgetPlacement:
    if target == HomeTabTarget.BIG_SCREEN:
        return BigScreenHomeTabWidgetPlacement.empty()
    else:
        return SmallScreenHomeTabWidgetPlacement.empty()
