/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailAddress } from './EmailAddress';
import type { PasswordPlain } from './PasswordPlain';

export type LoginArgs = {
    email_address: EmailAddress;
    password: PasswordPlain;
};

