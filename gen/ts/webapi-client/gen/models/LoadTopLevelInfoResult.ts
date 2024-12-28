/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AppCore } from './AppCore';
import type { AppPlatform } from './AppPlatform';
import type { AppShell } from './AppShell';
import type { Env } from './Env';
import type { Hosting } from './Hosting';
import type { ProjectName } from './ProjectName';
import type { ScheduleStreamName } from './ScheduleStreamName';
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
    deafult_workspace_name: WorkspaceName;
    default_first_schedule_stream_name: ScheduleStreamName;
    default_root_project_name: ProjectName;
    workspace_feature_flag_controls: WorkspaceFeatureFlagsControls;
    default_workspace_feature_flags: Record<string, boolean>;
    workspace_feature_hack: WorkspaceFeature;
    user?: (User | null);
    user_score_overview?: (UserScoreOverview | null);
    workspace?: (Workspace | null);
    user_feature_hack?: (UserFeature | null);
    app_core_hack?: (AppCore | null);
    app_shell_hack?: (AppShell | null);
    app_platform_hack?: (AppPlatform | null);
};

