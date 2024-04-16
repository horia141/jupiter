/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ClearAllArgs } from '../models/ClearAllArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class TestHelperService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for clearing all branch and leaf type entities.
     * The command for clearing all branch and leaf type entities.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public clearAll(
        requestBody?: ClearAllArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/clear-all',
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
