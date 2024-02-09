/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocName } from './DocName';
import type { EntityId } from './EntityId';
export type DocUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: DocName;
    };
};

