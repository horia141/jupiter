/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { SmartListTagName } from './SmartListTagName';

export type SmartListTagCreateArgs = {
    smart_list_ref_id: EntityId;
    tag_name: SmartListTagName;
};
