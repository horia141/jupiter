/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { ProjectName } from './ProjectName';
import type { Timestamp } from './Timestamp';
/**
 * The project.
 */
export type Project = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: ProjectName;
    project_collection_ref_id: string;
    parent_project_ref_id?: (EntityId | null);
    order_of_child_projects: Array<EntityId>;
};

