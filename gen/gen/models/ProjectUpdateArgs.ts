/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { ProjectName } from './ProjectName';
export type ProjectUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: ProjectName;
    };
};

