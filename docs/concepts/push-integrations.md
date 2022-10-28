# Push Integrations

Jupiter offers support for integrating with a number of external tools such as Slack, GMail,
Google Calendar, generic email, and others, via the lightweight _push integrations_ model.

This relies on personal automation services such as [Zapier](https://zapier.com) or
[IFTTT](https://ifttt.com) which can connect to both the external tools and to Notion.

There is the need for using an account on these services, and some manual configuration work on your
behalf. The various tutorials and how-tos should cover things in detail.

Jupiter creates the Notion-side structures to allow for these integrations to work, does the
necessary bookkeeping to keep everything tidy, and affects the rest of the entities in the
specific ways of each integration.

The kind of behaviors which are allowed are:

* Creating [inbox tasks](./inbox-tasks.md) from [Slack messages](./slack-tasks.md). This is very
  useful to represent the work coming in via Slack from your colleagues in the framework of Jupiter.
* Creating inbox tasks from [email messages](./email-tasks.md). Email is
  another big source of work. And indeed, the concept of an inbox from tasks is lifted straight from
  electronic mail lingo.
* Creating [vacations](./vacations.md) from [Google Calendar events](./calendar-events.md).
* Creating inbox tasks from calendar events matching a certain pattern. This is very useful to
  represent specific types of meetings as tasks.

In exchange you get a very versatile and extensible framework. Indeed, as long as you can match the
push integration structure, and Zapier or IFTTT have a connector, you can use any data source.
Microsoft Teams instead of Slack, or Outlook instead of Google Calendar, for example.

The _big limitation_ of push integrations is that they are one way. Although there are certainly
designs which would allow two-way communication via personal automation services, this aspect is yet
unexplored.
