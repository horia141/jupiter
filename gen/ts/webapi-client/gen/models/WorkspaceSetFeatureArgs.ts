/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WorkspaceFeature } from './WorkspaceFeature';

/**
 * Arguments for setting a feature in the workspace.
 */
export type WorkspaceSetFeatureArgs = {
    feature: WorkspaceFeature;
    value: boolean;
};

