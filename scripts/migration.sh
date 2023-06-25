#!/bin/bash

set -ex

alembic --config ./core/migrations/alembic.ini upgrade head
