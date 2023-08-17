/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { TagName } from './TagName';

export type SmartListTagUpdateArgs = {
    ref_id: EntityId;
    tag_name: {
        should_change: boolean;
        value?: TagName;
    };
};

