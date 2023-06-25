/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { ResetPasswordArgs } from '../models/ResetPasswordArgs';
import type { ResetPasswordResult } from '../models/ResetPasswordResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AuthService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Change Password
     * Change password.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changePassword(
        requestBody: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/auth/change-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Reset Password
     * Reset password.
     * @param requestBody
     * @returns ResetPasswordResult Successful Response
     * @throws ApiError
     */
    public resetPassword(
        requestBody: ResetPasswordArgs,
    ): CancelablePromise<ResetPasswordResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/auth/reset-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
