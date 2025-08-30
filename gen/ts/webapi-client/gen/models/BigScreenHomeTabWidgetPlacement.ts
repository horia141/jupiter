/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { HomeTabWidgetPlacementSection } from './HomeTabWidgetPlacementSection';
/**
 * The placement of widgets on a tab for big screen.
 */
export type BigScreenHomeTabWidgetPlacement = {
    kind: BigScreenHomeTabWidgetPlacement.kind;
    matrix: Array<Array<(EntityId | null)>>;
    sections: Array<HomeTabWidgetPlacementSection>;
};
export namespace BigScreenHomeTabWidgetPlacement {
    export enum kind {
        BIG_SCREEN = 'big-screen',
    }
}

