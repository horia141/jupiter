/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { JournalSource } from './JournalSource';
import type { ParentLink } from './ParentLink';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { ReportPeriodResult } from './ReportPeriodResult';
import type { Timestamp } from './Timestamp';

export type Journal = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    journal_collection: ParentLink;
    source: JournalSource;
    right_now: ADate;
    period: RecurringTaskPeriod;
    timeline: string;
    report: ReportPeriodResult;
};

