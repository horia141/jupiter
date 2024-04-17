/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { PersonBirthday } from './PersonBirthday';
import type { PersonName } from './PersonName';
import type { PersonRelationship } from './PersonRelationship';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

/**
 * Person create args..
 */
export type PersonCreateArgs = {
    name: PersonName;
    relationship: PersonRelationship;
    catch_up_period?: (RecurringTaskPeriod | null);
    catch_up_eisen?: (Eisen | null);
    catch_up_difficulty?: (Difficulty | null);
    catch_up_actionable_from_day?: (RecurringTaskDueAtDay | null);
    catch_up_actionable_from_month?: (RecurringTaskDueAtMonth | null);
    catch_up_due_at_day?: (RecurringTaskDueAtDay | null);
    catch_up_due_at_month?: (RecurringTaskDueAtMonth | null);
    birthday?: (PersonBirthday | null);
};

