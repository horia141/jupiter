/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmailAddress } from './EmailAddress';
import type { PasswordNewPlain } from './PasswordNewPlain';
import type { RecoveryTokenPlain } from './RecoveryTokenPlain';
export type ResetPasswordArgs = {
    email_address: EmailAddress;
    recovery_token: RecoveryTokenPlain;
    new_password: PasswordNewPlain;
    new_password_repeat: PasswordNewPlain;
};

