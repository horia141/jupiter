# Vacations

A _vacation_ is a set period of time when some scheduled tasks aren't scheduled. These are
essentially chores that do not have the _must do_ attribute set.

Vacations are attached to the workspace. You can see the vacations in
the `Vacations` left-hand menu tab. An example:

![Vacations Overview](../assets/vacations-overview.png)

Alternatively you can see vacations via `vacation-show` in the CLI.

## Vacations Properties

A vacation has a name.

The start date is the time when the vacation starts, and tasks should not be generated. It should be before the
end date.

The end date is the time when the vacation end, and tasks should again be generated. It should be after the
start date.

## Vacations Interactions Summary

In the web app you can change the properties of a vacation by clicking on it in the view:

![Vacations Update](../assets/vacations-update.png)

In the CLI app you can:

* Create a vacation via `vacation-create`.
* Archive a vacation via `vacation-archive`.
* Change the name, start date or end date of a vacations via `vacation-update`.
* See a summary of all the vacations via `vacation-show`.
