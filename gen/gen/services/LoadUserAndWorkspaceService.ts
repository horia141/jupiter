/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoadUserAndWorkspaceArgs } from '../models/LoadUserAndWorkspaceArgs';
import type { LoadUserAndWorkspaceResult } from '../models/LoadUserAndWorkspaceResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class LoadUserAndWorkspaceService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Load User And Workspace
     * Load a user and workspace if they exist, or signal that it doesn't.
     * @param requestBody
     * @returns LoadUserAndWorkspaceResult Successful Response
     * @throws ApiError
     */
    public loadUserAndWorkspace(
        requestBody: LoadUserAndWorkspaceArgs,
    ): CancelablePromise<LoadUserAndWorkspaceResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/load-user-and-workspace',
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
