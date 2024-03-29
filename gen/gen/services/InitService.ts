/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InitArgs } from '../models/InitArgs';
import type { InitResult } from '../models/InitResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class InitService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * UseCase for initialising the workspace.
     * UseCase for initialising the workspace.
     * @param requestBody The input data
     * @returns InitResult Successful response
     * @throws ApiError
     */
    public init(
        requestBody?: InitArgs,
    ): CancelablePromise<InitResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/init',
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
