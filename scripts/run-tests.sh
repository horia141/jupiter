#!/bin/bash

set -ex

# TODO(horia141): find out why the hell poetry run doesn't work here 
pytest src/core/tests
