/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetSummariesArgs } from '../models/GetSummariesArgs';
import type { ModelGetSummariesResult } from '../models/ModelGetSummariesResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class GetSummariesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The use case for retrieving summaries about entities.
     * The use case for retrieving summaries about entities.
     * @param requestBody
     * @returns ModelGetSummariesResult Successful Response
     * @throws ApiError
     */
    public getSummaries(
        requestBody: GetSummariesArgs,
    ): CancelablePromise<ModelGetSummariesResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/get-summaries',
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
