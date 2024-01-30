/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailAddress } from './EmailAddress';
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { ProjectName } from './ProjectName';
import type { Timezone } from './Timezone';
import type { UserFeature } from './UserFeature';
import type { UserName } from './UserName';
import type { WorkspaceFeature } from './WorkspaceFeature';
import type { WorkspaceName } from './WorkspaceName';

export type InitArgs = {
    user_email_address: EmailAddress;
    user_name: UserName;
    user_timezone: Timezone;
    user_feature_flags: Array<UserFeature>;
    auth_password: PasswordNewPlain;
    auth_password_repeat: PasswordNewPlain;
    workspace_name: WorkspaceName;
    workspace_first_project_name: ProjectName;
    workspace_feature_flags: Array<WorkspaceFeature>;
};

