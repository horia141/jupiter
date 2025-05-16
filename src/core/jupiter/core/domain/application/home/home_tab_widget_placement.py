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
    matrix: list[list[EntityId | None]]
    sections: list[HomeTabWidgetPlacementSection]

    @staticmethod
    def empty() -> "BigScreenHomeTabWidgetPlacement":
        matrix = BigScreenHomeTabWidgetPlacement._compile_sections([])
        return BigScreenHomeTabWidgetPlacement(
            kind="big-screen", matrix=matrix, sections=[]
        )

    def add_widget(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "BigScreenHomeTabWidgetPlacement":
        """Add a widget to the placement."""
        new_sections = [
            *self.sections,
            HomeTabWidgetPlacementSection(widget_ref_id, geometry),
        ]
        new_matrix = BigScreenHomeTabWidgetPlacement._compile_sections(new_sections)
        return BigScreenHomeTabWidgetPlacement(
            kind=self.kind, matrix=new_matrix, sections=new_sections
        )

    def remove_widget(
        self,
        widget_ref_id: EntityId,
    ) -> "BigScreenHomeTabWidgetPlacement":
        """Remove a widget from the placement."""
        new_sections = [
            section for section in self.sections if section.ref_id != widget_ref_id
        ]
        new_matrix = BigScreenHomeTabWidgetPlacement._compile_sections(new_sections)
        return BigScreenHomeTabWidgetPlacement(
            kind=self.kind, matrix=new_matrix, sections=new_sections
        )

    def move_widget_to(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "BigScreenHomeTabWidgetPlacement":
        """Move a widget to a new position."""
        new_sections = [
            section for section in self.sections if section.ref_id != widget_ref_id
        ]
        new_sections.append(HomeTabWidgetPlacementSection(widget_ref_id, geometry))
        new_matrix = BigScreenHomeTabWidgetPlacement._compile_sections(new_sections)
        return BigScreenHomeTabWidgetPlacement(
            kind=self.kind, matrix=new_matrix, sections=new_sections
        )

    @staticmethod
    def _compile_sections(
        sections: list[HomeTabWidgetPlacementSection],
    ) -> list[list[EntityId | None]]:
        """Compile sections into a matrix, validating the layout."""
        for section in sections:
            if section.geometry.col < 0 or section.geometry.col > 2:
                raise InputValidationError(
                    f"Column position must be between 0-2, got {section.geometry.col}"
                )

        sections_by_id = {section.ref_id: section for section in sections}

        # Build the matrix
        max_row = (
            max(
                section.geometry.row
                + _buffer_from_dimension(section.geometry.dimension)
                for section in sections
            )
            if len(sections) > 0
            else _buffer_from_dimension(WidgetDimension.DIM_1x1)
        )
        matrix_c1: list[EntityId | None] = [None] * max_row
        matrix_c2: list[EntityId | None] = [None] * max_row
        matrix_c3: list[EntityId | None] = [None] * max_row
        matrix: list[list[EntityId | None]] = [matrix_c1, matrix_c2, matrix_c3]
        for section in sections:
            for row_idx in range(
                section.geometry.row,
                section.geometry.row + section.geometry.dimension.rows,
            ):
                for col_idx in range(
                    section.geometry.col,
                    section.geometry.col + section.geometry.dimension.cols,
                ):
                    if matrix[col_idx][row_idx] is not None:
                        raise InputValidationError(
                            f"Widget {section.ref_id} overlaps with {matrix[col_idx][row_idx]}"
                        )
                    matrix[col_idx][row_idx] = section.ref_id

        # Check that kx* widgets are last in their columns
        for col in matrix:
            for row_idx, widget_id in enumerate(col):
                if widget_id is not None:
                    section = sections_by_id[widget_id]
                    if section.geometry.dimension.is_k_sized:
                        # Check no widgets after this in the column
                        if any(other_id is not None for other_id in col[row_idx + 1 :]):
                            raise InputValidationError(
                                f"Widget {widget_id} with k-sized dimension must be last in its column"
                            )

        return matrix


@value
class SmallScreenHomeTabWidgetPlacement(HomeTabWidgetPlacement):
    """The placement of widgets on a tab for small screen."""

    kind: Literal["small-screen"]
    matrix: list[EntityId | None]
    sections: list[HomeTabWidgetPlacementSection]

    @staticmethod
    def empty() -> "SmallScreenHomeTabWidgetPlacement":
        matrix = SmallScreenHomeTabWidgetPlacement._compile_sections([])
        return SmallScreenHomeTabWidgetPlacement(
            kind="small-screen", matrix=matrix, sections=[]
        )

    def add_widget(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "SmallScreenHomeTabWidgetPlacement":
        """Add a widget to the placement."""
        if geometry.dimension.cols != 1:
            raise InputValidationError(
                f"Dimension {geometry.dimension} is not allowed for small screen"
            )
        new_sections = [
            *self.sections,
            HomeTabWidgetPlacementSection(widget_ref_id, geometry),
        ]
        new_matrix = SmallScreenHomeTabWidgetPlacement._compile_sections(new_sections)
        return SmallScreenHomeTabWidgetPlacement(
            kind=self.kind, matrix=new_matrix, sections=new_sections
        )

    def remove_widget(
        self,
        widget_ref_id: EntityId,
    ) -> "SmallScreenHomeTabWidgetPlacement":
        """Remove a widget from the placement."""
        new_sections = [
            section for section in self.sections if section.ref_id != widget_ref_id
        ]
        new_matrix = SmallScreenHomeTabWidgetPlacement._compile_sections(new_sections)
        return SmallScreenHomeTabWidgetPlacement(
            kind=self.kind, matrix=new_matrix, sections=new_sections
        )

    def move_widget_to(
        self,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "SmallScreenHomeTabWidgetPlacement":
        """Move a widget to a new position."""
        if geometry.dimension.cols != 1:
            raise InputValidationError(
                f"Dimension {geometry.dimension} is not allowed for small screen"
            )
        new_sections = [
            section for section in self.sections if section.ref_id != widget_ref_id
        ]
        new_sections.append(HomeTabWidgetPlacementSection(widget_ref_id, geometry))
        new_matrix = SmallScreenHomeTabWidgetPlacement._compile_sections(new_sections)
        return SmallScreenHomeTabWidgetPlacement(
            kind=self.kind, matrix=new_matrix, sections=new_sections
        )

    @staticmethod
    def _compile_sections(
        sections: list[HomeTabWidgetPlacementSection],
    ) -> list[EntityId | None]:
        """Compile sections into a matrix, validating the layout."""
        for section in sections:
            if section.geometry.col != 0:
                raise InputValidationError(
                    f"Column position must be 0, got {section.geometry.col}"
                )

        sections_by_id = {section.ref_id: section for section in sections}

        # Build the matrix
        max_row = (
            max(
                section.geometry.row
                + _buffer_from_dimension(section.geometry.dimension)
                for section in sections
            )
            if len(sections) > 0
            else _buffer_from_dimension(WidgetDimension.DIM_1x1)
        )
        matrix: list[EntityId | None] = [None] * max_row
        for section in sections:
            for row in range(
                section.geometry.row,
                section.geometry.row + section.geometry.dimension.rows,
            ):
                if matrix[row] is not None:
                    raise InputValidationError(
                        f"Widget {section.ref_id} overlaps with {matrix[row]}"
                    )
                matrix[row] = section.ref_id

        # Check that kx* widgets are last in their rows
        # Check that k-sized widgets are followed by None values only
        for i, widget_id in enumerate(matrix):
            if widget_id is not None:
                section = sections_by_id[widget_id]
                if section.geometry.dimension.is_k_sized:
                    # Verify no widgets exist after this one
                    if any(id is not None for id in matrix[i+1:]):
                        raise InputValidationError(
                            f"Widget {widget_id} with k-sized dimension must be last in the layout"
                        )

        return matrix


OneOfHomeTabWidgetPlacement = (
    BigScreenHomeTabWidgetPlacement | SmallScreenHomeTabWidgetPlacement
)


def build_home_tab_widget_placement(
    target: HomeTabTarget,
) -> OneOfHomeTabWidgetPlacement:
    if target == HomeTabTarget.BIG_SCREEN:
        return BigScreenHomeTabWidgetPlacement.empty()
    else:
        return SmallScreenHomeTabWidgetPlacement.empty()


def _buffer_from_dimension(dimension: WidgetDimension) -> int:
    if dimension.is_k_sized:
        return 3
    else:
        return dimension.rows + 2
