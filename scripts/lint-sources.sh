#!/bin/bash

set -ex

pylint ./src
pyflakes ./src