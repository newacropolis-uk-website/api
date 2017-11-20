#!/bin/bash
set +e

ENV=development
www_dir="www-$ENV"

port=5000

if [ ! -z "$1" ]; then
    www_dir="www-$1"
    cd $www_dir
    port="$(python app/config.py -e $1)"

    ENV=$1
fi

# kill any existing services running on port
fuser -k -n tcp $port

echo "hosting on $www_dir"

DATABASE_URL_ENV="\${DATABASE_URL_$ENV}"

eval "DATABASE_URL=$DATABASE_URL_ENV"

if psql -lqt | cut -d \| -f 1 | grep -qw ${DATABASE_URL##*/}; then
  echo ${DATABASE_URL##*/} 'already exists'
else
  createdb ${DATABASE_URL##*/}
  echo ${DATABASE_URL##*/} 'created'
fi

if [ -z "$VIRTUAL_ENV" ] && [ -d venv ]; then
  echo 'activate venv'
  source ./venv/bin/activate
fi

python app.py db upgrade

if [ "$2" = "gunicorn" -o "$1" = "gunicorn" ]; then
  export APP_SERVER=gunicorn
  NAME="na_api"
  FLASKDIR=app
  SOCKFILE=sock
  USER=root
  GROUP=root
  NUM_WORKERS=3
  
  echo "Starting $NAME"
  
  # Create the run directory if it doesn't exist
  RUNDIR=$(dirname $SOCKFILE)
  test -d $RUNDIR || mkdir -p $RUNDIR
  
  # Start your gunicorn
  exec gunicorn wsgi -b 0.0.0.0:$port \
    --access-logfile logs/gunicorn.log \
    --error-logfile logs/gunicorn.error.log \
    --name $NAME \
    --workers $NUM_WORKERS \
    # --user=$USER --group=$GROUP \
    # --bind=unix:$SOCKFILE
    --log-level DEBUG \
    --reload
else
  export APP_SERVER=flask
  python app.py runserver --port $port

if [ $www_dir != "www" ]; then
    echo "running on " $ENV
    exit 0
fi
