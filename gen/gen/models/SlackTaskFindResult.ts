/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Project } from './Project';
import type { SlackTaskFindResultEntry } from './SlackTaskFindResultEntry';

export type SlackTaskFindResult = {
    generation_project: Project;
    entries: Array<SlackTaskFindResultEntry>;
};

