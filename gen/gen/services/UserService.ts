/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserLoadArgs } from '../models/UserLoadArgs';
import type { UserLoadResult } from '../models/UserLoadResult';
import type { UserUpdateArgs } from '../models/UserUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class UserService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Update User
     * Update a user.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateUser(
        requestBody: UserUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/user/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load User
     * Load a user.
     * @param requestBody
     * @returns UserLoadResult Successful Response
     * @throws ApiError
     */
    public loadUser(
        requestBody: UserLoadArgs,
    ): CancelablePromise<UserLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/user/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
