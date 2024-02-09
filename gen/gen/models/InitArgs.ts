/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmailAddress } from './EmailAddress';
import type { EntityName } from './EntityName';
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { ProjectName } from './ProjectName';
import type { Timezone } from './Timezone';
import type { UserFeature } from './UserFeature';
import type { WorkspaceFeature } from './WorkspaceFeature';
export type InitArgs = {
    user_email_address: EmailAddress;
    user_name: EntityName;
    user_timezone: Timezone;
    user_feature_flags: Array<UserFeature>;
    auth_password: PasswordNewPlain;
    auth_password_repeat: PasswordNewPlain;
    workspace_name: EntityName;
    workspace_first_project_name: ProjectName;
    workspace_feature_flags: Array<WorkspaceFeature>;
};

