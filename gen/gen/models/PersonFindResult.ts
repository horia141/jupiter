/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PersonFindResultEntry } from './PersonFindResultEntry';
import type { Project } from './Project';

/**
 * PersonFindResult.
 */
export type PersonFindResult = {
    catch_up_project: Project;
    entries: Array<PersonFindResultEntry>;
};

