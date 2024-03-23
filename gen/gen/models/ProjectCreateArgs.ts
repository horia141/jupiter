/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ProjectName } from './ProjectName';

/**
 * Project create args.
 */
export type ProjectCreateArgs = {
    parent_project_ref_id?: EntityId;
    name: ProjectName;
};

