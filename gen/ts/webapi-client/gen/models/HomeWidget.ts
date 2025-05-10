/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { Timestamp } from './Timestamp';
import type { WidgetGeometry } from './WidgetGeometry';
import type { WidgetType } from './WidgetType';
/**
 * A widget on the home page.
 */
export type HomeWidget = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    home_tab_ref_id: string;
    the_type: WidgetType;
    geometry: WidgetGeometry;
};

