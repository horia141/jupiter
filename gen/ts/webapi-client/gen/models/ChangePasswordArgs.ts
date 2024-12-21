/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PasswordNewPlain } from './PasswordNewPlain';
import type { PasswordPlain } from './PasswordPlain';

/**
 * Change password args.
 */
export type ChangePasswordArgs = {
    current_password: PasswordPlain;
    new_password: PasswordNewPlain;
    new_password_repeat: PasswordNewPlain;
};

