/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HomeConfig } from './HomeConfig';
import type { HomeTab } from './HomeTab';
import type { WidgetTypeConstraints } from './WidgetTypeConstraints';
/**
 * The result of the home config load use case.
 */
export type HomeConfigLoadResult = {
    home_config: HomeConfig;
    tabs: Array<HomeTab>;
    widget_constraints: Record<string, WidgetTypeConstraints>;
};

