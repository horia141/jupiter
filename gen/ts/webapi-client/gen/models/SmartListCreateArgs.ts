/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { SmartListName } from './SmartListName';

/**
 * PersonFindArgs.
 */
export type SmartListCreateArgs = {
    name: SmartListName;
    icon?: (EntityIcon | null);
};

