# New Acropolis UK API  [![Build Status](https://travis-ci.org/NewAcropolis/api.svg?branch=master)](https://travis-ci.org/NewAcropolis/api) 
[![Coverage Status](https://coveralls.io/repos/github/NewAcropolis/api/badge.svg?branch=master)](https://coveralls.io/github/NewAcropolis/api?branch=master)

## Makefile

Run `make` to see list of available commands

## Running tests

On project path -

```shell
./scripts/run_tests.sh
```

## Starting the web application

On project path -

```shell
./scripts/run_app.sh [ENV]
```

Where ENV is -

`development - port 5000`
`https://<new acropolis url>/dev/`

`preview - port 4000`
`https://<new acropolis url>/preview/`

`live - port 8000`
`https://<new acropolis url>/`

## Logging

Logs are stored under the `logs` folder
