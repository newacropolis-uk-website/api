# New Acropolis UK API  [![Build Status](https://travis-ci.org/NewAcropolis/api.svg?branch=master)](https://travis-ci.org/NewAcropolis/api)
[![Coverage Status](https://coveralls.io/repos/github/NewAcropolis/api/badge.svg?branch=master)](https://coveralls.io/github/NewAcropolis/api?branch=master)

## Create virtualenv

A Virtual Environment is an isolated working copy of Python which
allows you to work on a specific project without worry of affecting other projects

Follow this guide to set up your virtualenv for this project;
https://virtualenvwrapper.readthedocs.io/en/latest/

## Using Makefile

Run `make dependencies` to install dependencies

Run `Make` to list available commands

## Set up environment variables

Copy `environment_sample.sh` and create an `environment.sh` file and fill in the env vars

```
export DATABASE_URL_development=<postgres url>
export API_development=<development endpoint, defaults to localhost:5000>
export ADMIN_CLIENT_ID=<admin client id>
export ADMIN_PASSWORD=<admin client password>
export ADMIN_CLIENT_SECRET=<admin client secret>
export JWT_SECRET=<secret key>
export PROJECT=<google project name>
export FRONTEND_ADMIN_URL=<URL for the frontend admin>
export API_BASE_URL=<URL for API>
export FRONTEND_URL=<URL for the frontend>
export IMAGES_URL=<URL for images>
# optional below
export EMAIL_DOMAIN=<email domain for admin users>
export ADMIN_USERS=<super admin emails comma separated>
export GOOGLE_APPLICATION_CREDENTIALS=<location of google credentials>
export GOOGLE_STORE=<name of google storage>
export PAYPAL_URL=<paypal url>
export PAYPAL_USER=<paypal seller account>
export PAYPAL_PASSWORD=<paypal password>
export PAYPAL_SIG=<paypal signature>
export EMAIL_PROVIDER_URL=<email provider url>
export EMAIL_PROVIDER_APIKEY=<email provider api key>
export CELERY_BROKER_URL=<celery broker URL, normally redis>
```

Run `source environment.sh` to make the parameters available

## Running tests

On project path -

```shell
./scripts/run_tests.sh
```

## Run integration tests

Run the api `make run`

While the application is running, run the `./integration_test.sh`

## Starting the web application

On project path -

```shell
./scripts/run_app.sh [ENV]
```

Where ENV is -

`development - port 5000`
`https://<new acropolis url>/dev/`

`preview`
`https://<new acropolis url>/preview/`

`live`
`https://<new acropolis url>/`

## Running imports

Imports can be run via `integration_test.sh`

### Import order

```
# import venues
./integration.sh -iv
# import speakers
./integration.sh -is
# import event types
./integration.sh -iet
# import events
./integration.sh -ie
# import articles
./integration.sh -ia
# import marketing
./integration.sh -ima
# import members
./integration.sh -ime
# import emails
./integration.sh -iem
```

### Importing images

Images have to be uploaded from the dev machine, after which they can be copied to other storage buckets using `gsutil` and `rsync`:

```
gsutil -m rsync -r -d -p gs://<dev storage name> gs://<target storage name>
```

## Logging

Logs are stored under the `logs` folder
