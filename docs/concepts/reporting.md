# Reporting

Reporting is currently the main tool for reflection on past achievements, good aspects, and weak spots. It is a
functionality in Jupiter, available only in the [CLI](jupiter-cli.md) so far, which allows you to gather stats and
other insights into how you're progression on your goals.

The command itself is called `report` and can be called as such:

```bash
$ jupiter report
Weekly as of 2020-08-31:
  Global:
    Inbox Tasks:
      Created: 86 (1 ad hoc) (0 from big plan) (85 from recurring task)
      Accepted: 83 (1 ad hoc) (0 from big plan) (82 from recurring task)
      Working: 9 (0 ad hoc) (0 from big plan) (9 from recurring task)
      Not Done: 2 (0 ad hoc) (0 from big plan) (2 from recurring task)
      Done: 17 (1 ad hoc) (0 from big plan) (16 from recurring task)
    Big Plans:
      Created: 0
      Accepted: 0
      Working: 0
      Not Done: 0
      Done: 1
      - Finish a big chunk of work
```

The numbers above are just an example, of course. But you can see a rough analysis of how many tasks were marked as done
or not done, as well as how many were created and accepted. Be warned that working has a "janky" definition here - it's
tasks not in any of the start or [end states](inbox-tasks.md) in the time interval being analyzed.

The command can do _a lot_ more however. Just as an example, here's a breakdown of this year's efforts at developing
some habits:

```bash
$ jupiter --period yearly --breakdown recurring-tasks --recurring-task-type habit
Yearly as of 2020-08-31:
  By Recurring Task:
    Perform strength exercise routine:
      Created: 109
      In Progress: 1
      Working: 0
      Not Done: 28 (26%)
      Done: 80 (73%)
      Completed Ratio: 99%
      Current Streak: 0
      Longest Streak: 17
      Streak Sizes (Max 1 Skip):
        1 => 1
        3 => 3
        6 => 1
        7 => 1
        8 => 1
        11 => 1
        13 => 1
        14 => 1
        19 => 1
      Streak Plot: XxXXXXXXXXXXXXXXXXX..X...XXX..XXXxXXXXXXX..XXXXxX.XXXXXXXxXXXXXX.XXXxXXXXXXXXX..XxX.XXXXXxX...XXxXXXXX...XXX?
    Walk more than 3000 steps:
      Created: 109
      In Progress: 1
      Working: 0
      Not Done: 8 (7%)
      Done: 100 (92%)
      Completed Ratio: 99%
      Current Streak: 0
      Longest Streak: 31
      Streak Sizes (Max 1 Skip):
        11 => 1
        12 => 1
        17 => 1
        29 => 1
        35 => 1
      Streak Plot: XXXXXxXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxXXX.XXXXXXXXXXXXXXXxXXXXXXXXXXXXX.XXXXXXXXXXxX.XXXXXXXXXXX?
```

It's again _example_ data, but you can see a lot more stats about the various recurring tasks, as well as a histogram
of streaks, and even a _streak plot_ showing how uniform you're with keeping to these habits.

The most important way you can slice the data is via the breakdowns (controlled by the `--breakdown` option). You can
ask to break down the standard counts from above on projects, time periods, big plans or recurring tasks.

Some things to note:

* You can filter by project, or even a particular big plan, or recurring task.
* You can ask for a report as of a particular date via the `--date` option.
* By default the command looks at the current week, but you can change the period via the `--period` option, allowing
  you to analyze the month, quarter, or even year.
* When you're breaking down by periods, use the `--sub-period` option to control the resolution of the breakdown. By
  default it's the next smallest period than the `--period` option.
* You can control if you want to look at only inbox tasks, or only big plans.
* Check the help for more options via `jupiter report --help`.
