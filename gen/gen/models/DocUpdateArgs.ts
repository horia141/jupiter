/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DocName } from './DocName';
import type { EntityId } from './EntityId';

/**
 * DocUpdate args.
 */
export type DocUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: DocName;
    };
};

