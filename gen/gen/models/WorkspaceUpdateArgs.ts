/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityName } from './EntityName';

export type WorkspaceUpdateArgs = {
    name: {
        should_change: boolean;
        value?: EntityName;
    };
};

