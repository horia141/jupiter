/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { PersonBirthday } from './PersonBirthday';
import type { PersonName } from './PersonName';
import type { PersonRelationship } from './PersonRelationship';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskDueAtTime } from './RecurringTaskDueAtTime';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

export type PersonUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: PersonName;
    };
    relationship: {
        should_change: boolean;
        value?: PersonRelationship;
    };
    catch_up_period: {
        should_change: boolean;
        value?: RecurringTaskPeriod;
    };
    catch_up_eisen: {
        should_change: boolean;
        value?: Eisen;
    };
    catch_up_difficulty: {
        should_change: boolean;
        value?: Difficulty;
    };
    catch_up_actionable_from_day: {
        should_change: boolean;
        value?: RecurringTaskDueAtDay;
    };
    catch_up_actionable_from_month: {
        should_change: boolean;
        value?: RecurringTaskDueAtMonth;
    };
    catch_up_due_at_time: {
        should_change: boolean;
        value?: RecurringTaskDueAtTime;
    };
    catch_up_due_at_day: {
        should_change: boolean;
        value?: RecurringTaskDueAtDay;
    };
    catch_up_due_at_month: {
        should_change: boolean;
        value?: RecurringTaskDueAtMonth;
    };
    birthday: {
        should_change: boolean;
        value?: PersonBirthday;
    };
};

