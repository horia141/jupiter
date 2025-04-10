/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoginArgs } from '../models/LoginArgs';
import type { LoginResult } from '../models/LoginResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class LoginService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Use case for logging in as a particular user.
     * Use case for logging in as a particular user.
     * @param requestBody The input data
     * @returns LoginResult Successful response
     * @throws ApiError
     */
    public login(
        requestBody?: LoginArgs,
    ): CancelablePromise<LoginResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/login',
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
