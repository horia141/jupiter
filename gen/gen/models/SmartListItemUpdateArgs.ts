/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { TagName } from './TagName';
import type { URL } from './URL';

export type SmartListItemUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: EntityName;
    };
    is_done: {
        should_change: boolean;
        value?: boolean;
    };
    tags: {
        should_change: boolean;
        value?: Array<TagName>;
    };
    url: {
        should_change: boolean;
        value?: URL;
    };
};

