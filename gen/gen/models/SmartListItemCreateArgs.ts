/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { SmartListTagName } from './SmartListTagName';
import type { URL } from './URL';

export type SmartListItemCreateArgs = {
    smart_list_ref_id: EntityId;
    name: EntityName;
    is_done: boolean;
    tag_names: Array<SmartListTagName>;
    url?: URL;
};

