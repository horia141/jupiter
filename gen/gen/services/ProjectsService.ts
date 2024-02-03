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
import type { ProjectRemoveArgs } from '../models/ProjectRemoveArgs';
import type { ProjectUpdateArgs } from '../models/ProjectUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ProjectsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for archiving a project.
     * The command for archiving a project.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public projectArchive(
        requestBody: ProjectArchiveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project-archive',
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
     * The command for creating a project.
     * The command for creating a project.
     * @param requestBody
     * @returns ProjectCreateResult Successful Response
     * @throws ApiError
     */
    public projectCreate(
        requestBody: ProjectCreateArgs,
    ): CancelablePromise<ProjectCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project-create',
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
     * The command for finding projects.
     * The command for finding projects.
     * @param requestBody
     * @returns ProjectFindResult Successful Response
     * @throws ApiError
     */
    public projectFind(
        requestBody: ProjectFindArgs,
    ): CancelablePromise<ProjectFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project-find',
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
     * Use case for loading a particular project.
     * Use case for loading a particular project.
     * @param requestBody
     * @returns ProjectLoadResult Successful Response
     * @throws ApiError
     */
    public projectLoad(
        requestBody: ProjectLoadArgs,
    ): CancelablePromise<ProjectLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project-load',
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
     * The command for removing a project.
     * The command for removing a project.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public projectRemove(
        requestBody: ProjectRemoveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project-remove',
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
     * The command for updating a project.
     * The command for updating a project.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public projectUpdate(
        requestBody: ProjectUpdateArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/project-update',
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
