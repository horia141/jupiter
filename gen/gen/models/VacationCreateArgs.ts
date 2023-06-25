/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { VacationName } from './VacationName';

export type VacationCreateArgs = {
    name: VacationName;
    start_date: ADate;
    end_date: ADate;
};

