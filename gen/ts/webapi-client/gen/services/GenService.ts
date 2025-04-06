/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GenDoArgs } from '../models/GenDoArgs';
import type { GenLoadRunsArgs } from '../models/GenLoadRunsArgs';
import type { GenLoadRunsResult } from '../models/GenLoadRunsResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class GenService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for generating new tasks.
     * The command for generating new tasks.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public genDo(
        requestBody?: GenDoArgs,
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
     * @param requestBody The input data
     * @returns GenLoadRunsResult Successful response
     * @throws ApiError
     */
    public genLoadRuns(
        requestBody?: GenLoadRunsArgs,
    ): CancelablePromise<GenLoadRunsResult> {
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
