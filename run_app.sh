#!/bin/bash
set +e

www_dir="www"

port=5000

if [ ! -z "$1" ]; then
    www_dir="$www_dir-$1"
    cd $www_dir
    port="$(python app/config.py -e $1)"

    # kill any existing services running on port
    fuser -k -n tcp $port
fi

echo "hosting on $www_dir"

if [ $www_dir != "www" ]; then
    python app.py runserver --port $port&
else
    python app.py runserver --port $port
fi

if [ $www_dir != "www" ]; then
    exit 0
fi
