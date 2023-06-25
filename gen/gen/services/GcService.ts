/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GCArgs } from '../models/GCArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class GcService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Garbage Collect
     * Garbage collect.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public garbageCollect(
        requestBody: GCArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gc',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
