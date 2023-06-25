/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { SmartListName } from './SmartListName';

export type SmartListUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: SmartListName;
    };
    icon: {
        should_change: boolean;
        value?: EntityIcon;
    };
};

