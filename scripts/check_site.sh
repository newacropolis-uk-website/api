#!/bin/bash
set -o pipefail

if [ ! -z "$1" ]; then
    api_url=$1
else
    api_url="http://localhost:5000/"
fi

echo $api_url

n=0
until [ $n -ge 5 ]
do
    info=$(curl -s -X GET "$api_url" | jq -r '.info')
    if [ ! -z "$info" ]; then
        break
    fi

    n=$[$n+1]

    echo "retry $n"
    sleep 10
done

if [ -z "$info" -o "$info" = "null" ]; then
    echo 'failed'
    exit 1
else
    echo $info
    echo 'success'
fi
