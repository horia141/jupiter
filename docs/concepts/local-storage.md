# Local Storage

Local storage is the name given to what is essentially the _master_ version of the data Jupiter manages - all the
inbox tasks, the big plans, the recurring tasks, the smart lists, metrics, stats about them, links to Notion etc.

It is managed by the [Jupiter CLI](jupiter-cli.md).

Right now, it's nothing more than a bunch of files in a directory. The [tutorial](../tutorial.md) handles setting it up,
but it's essentially a `mdkir` and `jupiter workspace-init` inside that directory.

At this point Jupiter does not do any special backup or replication of this data. It's up to you to do so. Git with
GitHub/GitLab is a good solution to use here, as essentially the data is just text files. But you can just as
easily use Dropbox/Google Drive/Apple Cloud or any other file sharing solution. You won't have an easy restore
option in case of mistakes though.
