/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { SmartListItemName } from './SmartListItemName';
import type { SmartListTagName } from './SmartListTagName';
import type { URL } from './URL';
export type SmartListItemCreateArgs = {
    smart_list_ref_id: EntityId;
    name: SmartListItemName;
    is_done: boolean;
    tag_names: Array<SmartListTagName>;
    url?: URL;
};

