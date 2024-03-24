/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Env } from './Env';
import type { Hosting } from './Hosting';
import type { ProjectName } from './ProjectName';
import type { User } from './User';
import type { UserFeature } from './UserFeature';
import type { UserFeatureFlagsControls } from './UserFeatureFlagsControls';
import type { UserScoreOverview } from './UserScoreOverview';
import type { Workspace } from './Workspace';
import type { WorkspaceFeature } from './WorkspaceFeature';
import type { WorkspaceFeatureFlagsControls } from './WorkspaceFeatureFlagsControls';
import type { WorkspaceName } from './WorkspaceName';

/**
 * Load user and workspace result.
 */
export type LoadTopLevelInfoResult = {
    env: Env;
    hosting: Hosting;
    user_feature_flag_controls: UserFeatureFlagsControls;
    default_user_feature_flags: Record<string, boolean>;
    user_feature_hack: UserFeature;
    deafult_workspace_name: WorkspaceName;
    default_root_project_name: ProjectName;
    workspace_feature_flag_controls: WorkspaceFeatureFlagsControls;
    default_workspace_feature_flags: Record<string, boolean>;
    workspace_feature_hack: WorkspaceFeature;
    user?: User;
    user_score_overview?: UserScoreOverview;
    workspace?: Workspace;
};

