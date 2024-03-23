/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ProjectName } from './ProjectName';

/**
 * Summary information about a project.
 */
export type ProjectSummary = {
    ref_id: EntityId;
    parent_project_ref_id?: EntityId;
    name: ProjectName;
};

