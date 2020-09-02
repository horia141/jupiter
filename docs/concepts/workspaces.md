# Workspace

All the work for life planning takes place in a _workspace_. When you use
`jupiter workspace-init` in a local directory, you’re starting up your workspace. The local
directory and its files, the Notion.so pages created, etc. are all part of the
workspace.

You can have multiple workspaces, and they can even share the same Notion
space/account, but realistically it makes sense to use just one. All further
concepts we discuss are _relative_ to the workspace.

Workspaces are created via the `jupiter workspace-init` command. `jupiter workspace-init` is idempotent, and is a good
way to update workspaces as newer versions of the tool appear.

After creating a workspace, you’ll see something like the following in the Notion
left hand bar - here with a couple of projects too at the top-level under “Plans”,
namely “Personal”, “Engineer 2.0”, “Work @Bolt”, etc:

![Workspace image](../assets/concepts-workspace.png)

## Workspace Properties

A workspace has a _name_. It is the name of the root page in Notion too.

The token is the secret used to access Notion. From time to time it expires, so it needs tob be updated here as well
The token can be obtained as described in the [tutorial section](https://github.com/horia141/jupiter/blob/master/docs
/tutorial.md).

The space id is specified when calling `workspace-init`. It identifies the Notion "space" where Jupiter will work. It
can't be changed after creation though.

## Workspace Interactions Summary

You can:

* Create a workspace via `workspace-init`
* Set the name of the workspace via `workspace-set-name` or editing the name in Notion directly
* Set the token of the workspace via `workspace-set-token`.
* Synchronise changes between the local store and Notion via `workspace-sync`.
* See a summary of the workspace via `workspace-show`.
