/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { HomeTabWidgetPlacementSection } from './HomeTabWidgetPlacementSection';
/**
 * The placement of widgets on a tab for small screen.
 */
export type SmallScreenHomeTabWidgetPlacement = {
    kind: SmallScreenHomeTabWidgetPlacement.kind;
    matrix: Array<(EntityId | null)>;
    sections: Array<HomeTabWidgetPlacementSection>;
};
export namespace SmallScreenHomeTabWidgetPlacement {
    export enum kind {
        SMALL_SCREEN = 'small-screen',
    }
}

