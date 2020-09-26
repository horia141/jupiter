# Roadmap

This is a rough roadmap of getting Jupiter to `v1.0.0`. By this point it should have a lot of useful features,
be stable and fast, and have sufficient supporting infrastructure (website, docs, installation methods, etc).

New features:

* Support metrics
* Support a journal
* Support habits as separated from chores
* Support a Rolodex
* Support megaplans
* Define visual identity
* Translate app and docs in one other language

Public infrastructure:

* Have different methods of installation
* Have data export functionality
* Have a public workspace with all outstanding work
* Setup a forum for discussions and support
* Setup a blog for announcement and marketing content

Quality:

* Switch from text files to SQLite storage
* Upgrade to Notion public API (when available)

Beyond this the plans get _ambitious_. Here's some product-wise plans:

* Build a server-like component, which will allow periodic syncs, gen, and gcs, as well as interaction with online
 services
* Build a graphical client as a counterpart to the CLI one, and an alternative to the Notion one
* Support integration with other Notion-like apps
* Allow task creation via email or chatbots
* Build a Slack app and allow control via Slack commands
* Integrate with Google calendar / iCal for task source, as well as to export a calendar with all the tasks
* Integrate with YouTube, Spotify, Apple Music, Amazon, etc for smart lists support, playlists creation, etc
* Build a hosting/SaaS setup for all of the above
