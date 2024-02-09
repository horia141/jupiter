/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserChangeFeatureFlagsArgs } from '../models/UserChangeFeatureFlagsArgs';
import type { UserLoadArgs } from '../models/UserLoadArgs';
import type { UserLoadResult } from '../models/UserLoadResult';
import type { UserUpdateArgs } from '../models/UserUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class UsersService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Usecase for changing the feature flags for the user.
     * Usecase for changing the feature flags for the user.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public userChangeFeatureFlags(
        requestBody: UserChangeFeatureFlagsArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/user-change-feature-flags',
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
     * The command for loading the current user.
     * The command for loading the current user.
     * @param requestBody
     * @returns UserLoadResult Successful Response
     * @throws ApiError
     */
    public userLoad(
        requestBody: UserLoadArgs,
    ): CancelablePromise<UserLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/user-load',
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
     * The command for updating a user's properties.
     * The command for updating a user's properties.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public userUpdate(
        requestBody: UserUpdateArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/user-update',
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
