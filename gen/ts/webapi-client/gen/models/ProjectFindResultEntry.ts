/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { Project } from './Project';

/**
 * A single project result.
 */
export type ProjectFindResultEntry = {
    project: Project;
    note?: (Note | null);
};

