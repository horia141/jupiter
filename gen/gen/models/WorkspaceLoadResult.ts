/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Project } from './Project';
import type { Workspace } from './Workspace';

/**
 * PersonFindResult object.
 */
export type WorkspaceLoadResult = {
    workspace: Workspace;
    default_project: Project;
};

