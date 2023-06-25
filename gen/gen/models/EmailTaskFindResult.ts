/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailTaskFindResultEntry } from './EmailTaskFindResultEntry';
import type { Project } from './Project';

export type EmailTaskFindResult = {
    generation_project: Project;
    entries: Array<EmailTaskFindResultEntry>;
};

