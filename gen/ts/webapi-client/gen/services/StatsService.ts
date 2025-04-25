/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StatsDoArgs } from '../models/StatsDoArgs';
import type { StatsLoadRunsArgs } from '../models/StatsLoadRunsArgs';
import type { StatsLoadRunsResult } from '../models/StatsLoadRunsResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StatsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for computing stats.
     * The command for computing stats.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public statsDo(
        requestBody?: StatsDoArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/stats-do',
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
     * Load previous runs of stats computation.
     * Load previous runs of stats computation.
     * @param requestBody The input data
     * @returns StatsLoadRunsResult Successful response
     * @throws ApiError
     */
    public statsLoadRuns(
        requestBody?: StatsLoadRunsArgs,
    ): CancelablePromise<StatsLoadRunsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/stats-load-runs',
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
