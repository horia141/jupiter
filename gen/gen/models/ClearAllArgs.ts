/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { PasswordPlain } from './PasswordPlain';
import type { Timezone } from './Timezone';
import type { UserFeature } from './UserFeature';
import type { WorkspaceFeature } from './WorkspaceFeature';

export type ClearAllArgs = {
    user_name: EntityName;
    user_timezone: Timezone;
    user_feature_flags: Array<UserFeature>;
    auth_current_password: PasswordPlain;
    auth_new_password: PasswordNewPlain;
    auth_new_password_repeat: PasswordNewPlain;
    workspace_name: EntityName;
    workspace_default_project_ref_id: EntityId;
    workspace_feature_flags: Array<WorkspaceFeature>;
};

