/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';

export type DocUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: EntityName;
    };
};

