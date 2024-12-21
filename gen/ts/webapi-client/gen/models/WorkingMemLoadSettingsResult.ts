/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Project } from './Project';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

/**
 * WorkingMemLoadSettings results.
 */
export type WorkingMemLoadSettingsResult = {
    generation_period: RecurringTaskPeriod;
    cleanup_project: Project;
};

