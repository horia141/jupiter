/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoadTopLevelInfoArgs } from '../models/LoadTopLevelInfoArgs';
import type { LoadTopLevelInfoResult } from '../models/LoadTopLevelInfoResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class LoadTopLevelInfoService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Load Top Level Info
     * Load a user and workspace if they exist and other assorted data.
     * @param requestBody
     * @returns LoadTopLevelInfoResult Successful Response
     * @throws ApiError
     */
    public loadTopLevelInfo(
        requestBody: LoadTopLevelInfoArgs,
    ): CancelablePromise<LoadTopLevelInfoResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/load-top-level-info',
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
