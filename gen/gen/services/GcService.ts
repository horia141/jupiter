/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GCDoArgs } from '../models/GCDoArgs';
import type { GCLoadRunsArgs } from '../models/GCLoadRunsArgs';
import type { ModelGCLoadRunsResult } from '../models/ModelGCLoadRunsResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class GcService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for doing a garbage collection run.
     * The command for doing a garbage collection run.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public gcDo(
        requestBody: GCDoArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gc-do',
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
     * Load previous runs of GC.
     * Load previous runs of GC.
     * @param requestBody
     * @returns ModelGCLoadRunsResult Successful Response
     * @throws ApiError
     */
    public gcLoadRuns(
        requestBody: GCLoadRunsArgs,
    ): CancelablePromise<ModelGCLoadRunsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gc-load-runs',
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
