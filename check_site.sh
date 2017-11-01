#!/bin/bash
set -o pipefail

if [ ! -z "$1" ]; then
    api_url=$1
else
    api_url="http://localhost:5000/"
fi

export info=$(curl -X GET "$api_url" | jq -r '.info')

if [ -z "$info" ]; then
    echo 'failed'
    # exit 1
else
    echo $info
    echo 'success'
    # exit 0
fi
