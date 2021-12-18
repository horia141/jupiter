#!/bin/bash

set -ex

alembic --config ./migrations/alembic.ini upgrade head