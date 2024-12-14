# Version 0.8.0

Launched on 2021/12/18

This version introduces:

* Added support for a "personal relationship manager" feature. Read more in the [PRM section](../concepts/persons.md).
* Entities which can be associated with a project, can now use a default project.
* Faster local -> Notion updates
* Moved some entities to SQLite storage from the text based one. It's faster and safer.
* Stopped syncing archived inbox tasks
* A massive refactoring of the code-base. Nothing was left untouched. The new code is
  easier to maintain and structurally better organized.
* Fixed high severity security issue with a `mkdocs` dependency
* Bugfix of metric entry sync which would clear the collection time on Notion side
* Bugfix of recurring task sync start date value being ignored if set on Notion side
* Bugfix of not syncing vacations sometimes
