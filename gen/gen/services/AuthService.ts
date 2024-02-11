/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { ResetPasswordResult } from '../models/ResetPasswordResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuthService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Use case for changing a password.
     * Use case for changing a password.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public changePassword(
        requestBody: ChangePasswordArgs,
    ): CancelablePromise<null> {
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
     * @returns ResetPasswordResult Successful Response
     * @throws ApiError
     */
    public resetPassword(): CancelablePromise<ResetPasswordResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/reset-password',
            errors: {
                406: `Feature Not Available`,
                410: `Workspace Or User Not Found`,
            },
        });
    }
}
