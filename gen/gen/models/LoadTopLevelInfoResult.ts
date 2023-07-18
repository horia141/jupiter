/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Env } from './Env';
import type { Feature } from './Feature';
import type { FeatureFlagsControls } from './FeatureFlagsControls';
import type { Hosting } from './Hosting';
import type { ProjectName } from './ProjectName';
import type { User } from './User';
import type { Workspace } from './Workspace';
import type { WorkspaceName } from './WorkspaceName';

export type LoadTopLevelInfoResult = {
    env: Env;
    hosting: Hosting;
    deafult_workspace_name: WorkspaceName;
    default_first_project_name: ProjectName;
    feature_flag_controls: FeatureFlagsControls;
    default_feature_flags: Record<string, boolean>;
    feature_hack: Feature;
    user?: User;
    workspace?: Workspace;
};

