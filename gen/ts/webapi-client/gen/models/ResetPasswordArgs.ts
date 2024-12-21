/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailAddress } from './EmailAddress';
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { RecoveryTokenPlain } from './RecoveryTokenPlain';

/**
 * Reset password args.
 */
export type ResetPasswordArgs = {
    email_address: EmailAddress;
    recovery_token: RecoveryTokenPlain;
    new_password: PasswordNewPlain;
    new_password_repeat: PasswordNewPlain;
};

