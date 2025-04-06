/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkspaceChangeFeatureFlagsArgs } from '../models/WorkspaceChangeFeatureFlagsArgs';
import type { WorkspaceLoadArgs } from '../models/WorkspaceLoadArgs';
import type { WorkspaceLoadResult } from '../models/WorkspaceLoadResult';
import type { WorkspaceUpdateArgs } from '../models/WorkspaceUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WorkspacesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Usecase for changing the feature flags for the workspace.
     * Usecase for changing the feature flags for the workspace.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public workspaceChangeFeatureFlags(
        requestBody?: WorkspaceChangeFeatureFlagsArgs,
    ): CancelablePromise<any> {
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
     * @param requestBody The input data
     * @returns WorkspaceLoadResult Successful response
     * @throws ApiError
     */
    public workspaceLoad(
        requestBody?: WorkspaceLoadArgs,
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
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public workspaceUpdate(
        requestBody?: WorkspaceUpdateArgs,
    ): CancelablePromise<any> {
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
