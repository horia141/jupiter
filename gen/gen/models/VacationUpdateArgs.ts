/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { VacationName } from './VacationName';

/**
 * PersonFindArgs.
 */
export type VacationUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: VacationName;
    };
    start_date: {
        should_change: boolean;
        value?: ADate;
    };
    end_date: {
        should_change: boolean;
        value?: ADate;
    };
};

