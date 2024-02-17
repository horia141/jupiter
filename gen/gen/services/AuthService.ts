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
     * Use case for changing a password.
     * Use case for changing a password.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public changePassword(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/change-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                406: `Feature Not Available`,
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Use case for reseting a password.
     * Use case for reseting a password.
     * @param requestBody The input data
     * @returns ResetPasswordResult Successful response
     * @throws ApiError
     */
    public resetPassword(
        requestBody?: ResetPasswordArgs,
    ): CancelablePromise<ResetPasswordResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/reset-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                406: `Feature Not Available`,
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
