/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WorkspaceName } from './WorkspaceName';

export type WorkspaceUpdateArgs = {
    name: {
        should_change: boolean;
        value?: WorkspaceName;
    };
};

