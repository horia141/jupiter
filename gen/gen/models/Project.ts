/* generated using openapi-typescript-codegen -- do no edit */
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
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    name: ProjectName;
    project_collection: string;
};

