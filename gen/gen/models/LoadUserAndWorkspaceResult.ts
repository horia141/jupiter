/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Env } from './Env';
import type { Feature } from './Feature';
import type { FeatureFlagsControls } from './FeatureFlagsControls';
import type { Hosting } from './Hosting';
import type { User } from './User';
import type { Workspace } from './Workspace';

export type LoadUserAndWorkspaceResult = {
    env: Env;
    hosting: Hosting;
    feature_flag_controls: FeatureFlagsControls;
    feature_hack: Feature;
    user?: User;
    workspace?: Workspace;
};

