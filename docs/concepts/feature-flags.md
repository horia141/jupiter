# Feature Flags

Jupiter can be quite overwhealming with its feature set and the various interaction modes between
each feature. At the same time, not everyone needs everything from the tool. Some might use it
primarily for short term work, others to plan out their life, while still others might focus on
tracking and recording things.

To account for this, the feature set visible in a workspace can be configured. Thus you can customize
your Jupiter experience, and keep only the features you need. And of course, you can add and remove
features at any time.

Indeed, **the backing data is never lost**. If you disable a feature, then all its associated data
and the various UIs and commands are hidden. When you re-enable it, you'll see the data again.

Conversely, no new data is generated via such processes as [generation](tasks-generation.md), nor is
data modified via other processes like [garbage collection](garbage-collection.md).

In the Web UI this lives under `Settings` and currently looks like:

![Feature Flags Overview](../assets/feature-flags-overview.png)

In the CLI you can view the feature flags with `workspace-show` and change them via
`workspace-change-feature-flags`.

