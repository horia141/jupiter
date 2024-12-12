# Version 0.5.1

Launched on 2020/10/18

This version introduces:

* Recurring tasks can have _active intervals_. Only during this interval will inbox tasks be generated. This can be
  open ended of course.
* Inbox tasks from recurring tasks now have the year included in the name.
* Reporting on habits also shows a "completion ratio" broken down by sub-periods.
* Inbox tasks now have an _actionable date_. They'll be visible to work on one week before this. Recurring tasks have
  been updated to allow generation of such fields too.
* Fix a timezone issue with recurring tasks generation.
* Fix an issue with smart list syncing which caused every smart list to contain every smart list item.
