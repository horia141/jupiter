/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { SmartListName } from './SmartListName';

export type SmartListSummary = {
    ref_id: EntityId;
    name: SmartListName;
    icon?: EntityIcon;
};

