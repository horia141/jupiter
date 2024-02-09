/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModelSearchResult } from '../models/ModelSearchResult';
import type { SearchArgs } from '../models/SearchArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class SearchService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Use case for free form searching through Jupiter.
     * Use case for free form searching through Jupiter.
     * @param requestBody
     * @returns ModelSearchResult Successful Response
     * @throws ApiError
     */
    public search(
        requestBody: SearchArgs,
    ): CancelablePromise<ModelSearchResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/search',
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
