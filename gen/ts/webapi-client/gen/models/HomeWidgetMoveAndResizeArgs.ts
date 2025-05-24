/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { WidgetDimension } from './WidgetDimension';
/**
 * The arguments for moving a home widget.
 */
export type HomeWidgetMoveAndResizeArgs = {
    ref_id: EntityId;
    row: number;
    col: number;
    dimension: WidgetDimension;
};

