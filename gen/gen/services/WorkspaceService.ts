/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkspaceChangeDefaultProjectArgs } from '../models/WorkspaceChangeDefaultProjectArgs';
import type { WorkspaceChangeFeatureFlagsArgs } from '../models/WorkspaceChangeFeatureFlagsArgs';
import type { WorkspaceLoadArgs } from '../models/WorkspaceLoadArgs';
import type { WorkspaceLoadResult } from '../models/WorkspaceLoadResult';
import type { WorkspaceUpdateArgs } from '../models/WorkspaceUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class WorkspaceService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Update Workspace
     * Update a workspace.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateWorkspace(
        requestBody: WorkspaceUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace/update',
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
     * Change Workspace Default Project
     * Change the default project for a workspace.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeWorkspaceDefaultProject(
        requestBody: WorkspaceChangeDefaultProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace/change-default-project',
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
     * Change Workspace Feature Flags
     * Change the feature flags for a workspace.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeWorkspaceFeatureFlags(
        requestBody: WorkspaceChangeFeatureFlagsArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace/change-feature-flags',
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
     * Load Workspace
     * Load a workspace.
     * @param requestBody
     * @returns WorkspaceLoadResult Successful Response
     * @throws ApiError
     */
    public loadWorkspace(
        requestBody: WorkspaceLoadArgs,
    ): CancelablePromise<WorkspaceLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace/load',
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
