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

export class WorkspacesService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * UseCase for changing the default project of a workspace.
     * UseCase for changing the default project of a workspace.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public workspaceChangeDefaultProject(
        requestBody: WorkspaceChangeDefaultProjectArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace-change-default-project',
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
     * Usecase for changing the feature flags for the workspace.
     * Usecase for changing the feature flags for the workspace.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public workspaceChangeFeatureFlags(
        requestBody: WorkspaceChangeFeatureFlagsArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace-change-feature-flags',
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
     * The command for loading workspaces.
     * The command for loading workspaces.
     * @param requestBody
     * @returns WorkspaceLoadResult Successful Response
     * @throws ApiError
     */
    public workspaceLoad(
        requestBody: WorkspaceLoadArgs,
    ): CancelablePromise<WorkspaceLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace-load',
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
     * UseCase for updating a workspace.
     * UseCase for updating a workspace.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public workspaceUpdate(
        requestBody: WorkspaceUpdateArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/workspace-update',
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
