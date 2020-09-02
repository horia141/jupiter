# Update An Expired Token

From time to time you'll encounter the following error message from Jupiter:

```bash
$ jupiter sync
/// Output omitted
The Notion connection's token has expired, please refresh it with 'workspace-set-token'
```

Due to the way the [Notion](https://notion.so) integration is done, you need to explicitly provide an "access token"
for Jupiter to be able to communicate with it. This token expires or is otherwise invalidated, and you need to manually
replace it.

In order to do this, you'll need to:

1. Go over to [notion.so](https://www.notion.so/) - the website. You should be seeing your space and anything you've
   setup there manually.
1. Open your browser's inspector. Refresh the page and wait for things to calm down.
1. Find the `/getPublicPageData` API call on the _Network_ tab.
1. In the headers field there will be a `cookie` set with the value `token`. That's your token for accessing the API.
   Write it down somewhere.

You can then set the token via the `workspace-set-token` command like so:

```bash
$ jupiter workspace-set-token --token THE_TOKEN_YOU_FOUND_ABOVE
$ jupiter sync  # It should just work
```

And that's it.
