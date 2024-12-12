# Version 0.1.0

Launched on 2020/03/15

This version introduces:

* A radical rework of the way interaction between the local space and Notion works. It's only visible in the workspace
  and vacations interactions now, but it'll seep into every facet. Basically there will be parity between what can be
  done with Notion and what via `thrive` CLI commands. Editing files will be a thing of the past as well. You can
  checkout the [tutorial](https://github.com/horia141/jupiter/blob/develop/docs/tutorial.md) and
  [concepts](https://github.com/horia141/jupiter/blob/develop/docs/concepts.md) for more details. But in short, now
  you can do something like `thrive vacations-add --name "Trip to Spain" --start-date 2020-05-03 --end-date 2020-05
  -18` and you'll get a new vacation with those coordinates.
* The above is the biggest "feature" in a while, hence the version is bumped from `0.0.5` to `0.1.0` - a minor bump!
* Technically, all scripts now reside in `./scripts`, rather than spread around Makefiles and GitHub actions