/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigScreenHomeTabWidgetPlacement } from './BigScreenHomeTabWidgetPlacement';
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { HomeTabTarget } from './HomeTabTarget';
import type { SmallScreenHomeTabWidgetPlacement } from './SmallScreenHomeTabWidgetPlacement';
import type { Timestamp } from './Timestamp';
/**
 * A tab on the home page.
 */
export type HomeTab = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    home_config_ref_id: string;
    target: HomeTabTarget;
    icon?: (EntityIcon | null);
    widget_placement: (BigScreenHomeTabWidgetPlacement | SmallScreenHomeTabWidgetPlacement);
};

