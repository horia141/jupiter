/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailAddress } from './EmailAddress';
import type { EntityName } from './EntityName';
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { Timezone } from './Timezone';

export type InitArgs = {
    user_email_address: EmailAddress;
    user_name: EntityName;
    user_timezone: Timezone;
    user_feature_flags: Record<string, boolean>;
    auth_password: PasswordNewPlain;
    auth_password_repeat: PasswordNewPlain;
    workspace_name: EntityName;
    workspace_first_project_name: EntityName;
    workspace_feature_flags: Record<string, boolean>;
};

