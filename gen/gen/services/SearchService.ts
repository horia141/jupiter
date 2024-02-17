/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SearchArgs } from '../models/SearchArgs';
import type { SearchResult } from '../models/SearchResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SearchService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for free form searching through Jupiter.
     * Use case for free form searching through Jupiter.
     * @param requestBody The input data
     * @returns SearchResult Successful response
     * @throws ApiError
     */
    public search(
        requestBody?: SearchArgs,
    ): CancelablePromise<SearchResult> {
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
