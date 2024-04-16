/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { Project } from './Project';

/**
 * ProjectLoadResult.
 */
export type ProjectLoadResult = {
    project: Project;
    note?: Note;
};

