/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { PasswordPlain } from './PasswordPlain';
import type { ProjectName } from './ProjectName';
import type { Timezone } from './Timezone';
import type { UserFeature } from './UserFeature';
import type { UserName } from './UserName';
import type { WorkspaceFeature } from './WorkspaceFeature';
import type { WorkspaceName } from './WorkspaceName';
/**
 * PersonFindArgs.
 */
export type ClearAllArgs = {
    user_name: UserName;
    user_timezone: Timezone;
    user_feature_flags?: (Array<UserFeature> | null);
    auth_current_password: PasswordPlain;
    auth_new_password: PasswordNewPlain;
    auth_new_password_repeat: PasswordNewPlain;
    workspace_name: WorkspaceName;
    workspace_root_project_name: ProjectName;
    workspace_feature_flags?: (Array<WorkspaceFeature> | null);
};

