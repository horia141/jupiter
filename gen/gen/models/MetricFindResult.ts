/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { MetricFindResponseEntry } from './MetricFindResponseEntry';
import type { Project } from './Project';

export type MetricFindResult = {
    collection_project: Project;
    entries: Array<MetricFindResponseEntry>;
};

