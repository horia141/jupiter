/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ClearAllArgs } from '../models/ClearAllArgs';
import type { RemoveAllArgs } from '../models/RemoveAllArgs';
import type { WorkspaceSetFeatureArgs } from '../models/WorkspaceSetFeatureArgs';
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
    /**
     * The command for removeing all branch and leaf type entities.
     * The command for removeing all branch and leaf type entities.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public removeAll(
        requestBody?: RemoveAllArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/remove-all',
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
     * Set a particular feature in the workspace.
     * Set a particular feature in the workspace.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public workspaceSetFeature(
        requestBody?: WorkspaceSetFeatureArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace-set-feature',
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
