/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class LoadTopLevelInfoService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for loading a user and workspace if they exist and other data too.
     * The command for loading a user and workspace if they exist and other data too.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public loadTopLevelInfo(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/load-top-level-info',
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
