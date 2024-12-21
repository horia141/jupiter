/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { PersonName } from './PersonName';

/**
 * Summary information about a person.
 */
export type PersonSummary = {
    ref_id: EntityId;
    name: PersonName;
};

