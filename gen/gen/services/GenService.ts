/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class GenService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for generating new tasks.
     * The command for generating new tasks.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public genDo(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gen-do',
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
     * Load previous runs of task generation.
     * Load previous runs of task generation.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public genLoadRuns(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gen-load-runs',
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
