/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { SmartListTagName } from './SmartListTagName';

export type SmartListTagUpdateArgs = {
    ref_id: EntityId;
    tag_name: {
        should_change: boolean;
        value?: SmartListTagName;
    };
};

