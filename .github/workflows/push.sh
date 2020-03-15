name: Push

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
     - uses: actions/checkout@v2
     - name: Install Deps Test
       run: pip3 install pylint
     - name: Lint Scripts
       run: ./scripts/lint-scripts.sh
     - name: Lint Sources
       run: ./scripts/lint-sources.sh
