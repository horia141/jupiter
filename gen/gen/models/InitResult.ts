/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthTokenExt } from './AuthTokenExt';
import type { RecoveryTokenPlain } from './RecoveryTokenPlain';
import type { User } from './User';
import type { Workspace } from './Workspace';
/**
 * Init use case result.
 */
export type InitResult = {
    new_user: User;
    new_workspace: Workspace;
    auth_token_ext: AuthTokenExt;
    recovery_token: RecoveryTokenPlain;
};

