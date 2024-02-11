/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WorkspacesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * UseCase for changing the default project of a workspace.
     * UseCase for changing the default project of a workspace.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public workspaceChangeDefaultProject(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public workspaceChangeFeatureFlags(
        requestBody?: ChangePasswordArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public workspaceLoad(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public workspaceUpdate(
        requestBody?: ChangePasswordArgs,
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
