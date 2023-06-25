# Overview

## Intro

Jupiter is a tool for _life planning_. It is _opinionated_ in how it approaches
this problem. The goal of this page is to document Jupiter's conceptual model
and how life planning is mapped to it.

There will be references made to the current implementation. But the concepts
are _separate_ from it, and could just as easily be implemented via pen & paper.

## The Concepts

As a quick reference, here is the list of the more important concepts:

* _Workspace_: the _place_ where all the work in Jupiter happens.
* _Task_: an atomic unit of work. This is normally something like "Congratulate
  Jeff on the speech", or "Buy new socks".
* _Habit_: a regular activity, usually one that is centered on _you_. Think
  "Walk 10K steps" or "Meditate for 5 minutes". A habit will generate a task periodically
   which needs to be acted upon.
* _Chore_: a regular activity, usually one that is imposed by the outside world. Think
  "Pay mortgage" or "Take car in for checks". A chore will generate a task periodically
  which needs to be acted upon.
* _Big plan_: a larger unit of work, consisting of multiple tasks. This is normally
  something like "Plan a family vacation", or "Get a talk accepted to a conference".
* _Project_: a larger and longer-term container for work. This is normally a
  neatly defined part such as "Personal" goals or "Career" goals, etc.
* _Smart list_: a list of things! It can record books to read, visited restaurants,
  movies to watch, etc.
* _Metric_: a measure of the evolution in time of some aspect of your life. Think
  weight, days gone to the gym, or marathons ran!
* _Person_: a family member, friend, acquaintance, etc you wish to keep in touch with, or
  otherwise know about in a more formal way.
* _Push Integrations_: lightweight integrations with external tools such as Slack, GMail,
  Outlook, generic email, etc. Done in a one-way fashion via these tools pushing work into Jupiter.

The rest of the document will cover each of these in greater detail.

## The Tool

Jupiter is _the tool_ that allows you to run your life by using the concepts above in certain ways.

You can interact with it via one of the [clients](clients.md) and in either [hosted or local mode](local-vs-hosted-mode.md)