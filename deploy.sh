#!/bin/sh

set +x

if [ -e environment.sh ]; then
    echo "source environment"
    source environment.sh
    basedir=.
else 
    if [ -z "$environment" ]; then
        echo "setting environment as preview"
        environment=preview
    fi 

    if [ $environment = preview  ]; then
        work_dir=test
    else
        work_dir=$environment
    fi

    basedir=~/workspace/$work_dir

fi

port="$(python $basedir/app/config.py -e $environment)"
if [ $port != 'No environment' ]; then

    src=$basedir/

    rsync -ravzhe ssh $src --exclude-from '.exclude' $webhost:www-$environment/; 

    eval "DATABASE_URL_ENV=\${DATABASE_URL_$environment}"

    echo starting app $environment on port $port
    ssh $webhost """
    cd www-$environment
    export DATABASE_URL_$environment=$DATABASE_URL_ENV
    export PGPASSWORD=$PGPASSWORD
    su root sh bootstrap.sh $environment
    sh run_app.sh $environment >&- 2>&- <&- &"""

else
    echo "$port"
    exit 1
fi
