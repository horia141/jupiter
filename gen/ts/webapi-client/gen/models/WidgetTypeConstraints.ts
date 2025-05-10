/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HomeTabTarget } from './HomeTabTarget';
import type { WidgetDimension } from './WidgetDimension';
/**
 * A constraints for a widget type.
 */
export type WidgetTypeConstraints = {
    allowed_dimensions: Array<WidgetDimension>;
    for_tab_target: Array<HomeTabTarget>;
};

