/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectArchiveArgs } from '../models/ProjectArchiveArgs';
import type { ProjectCreateArgs } from '../models/ProjectCreateArgs';
import type { ProjectCreateResult } from '../models/ProjectCreateResult';
import type { ProjectFindArgs } from '../models/ProjectFindArgs';
import type { ProjectFindResult } from '../models/ProjectFindResult';
import type { ProjectLoadArgs } from '../models/ProjectLoadArgs';
import type { ProjectLoadResult } from '../models/ProjectLoadResult';
import type { ProjectUpdateArgs } from '../models/ProjectUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ProjectService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Project
     * Create a project.
     * @param requestBody
     * @returns ProjectCreateResult Successful Response
     * @throws ApiError
     */
    public createProject(
        requestBody: ProjectCreateArgs,
    ): CancelablePromise<ProjectCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project/create',
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
     * Archive Project
     * Create a project.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveProject(
        requestBody: ProjectArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project/archive',
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
     * Update Project
     * Update a project.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateProject(
        requestBody: ProjectUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project/update',
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
     * Load Project
     * Load a project, filtering by id.
     * @param requestBody
     * @returns ProjectLoadResult Successful Response
     * @throws ApiError
     */
    public loadProject(
        requestBody: ProjectLoadArgs,
    ): CancelablePromise<ProjectLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project/load',
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
     * Find Project
     * Find a project, filtering by id.
     * @param requestBody
     * @returns ProjectFindResult Successful Response
     * @throws ApiError
     */
    public findProject(
        requestBody: ProjectFindArgs,
    ): CancelablePromise<ProjectFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project/find',
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
