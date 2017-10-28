#!/bin/bash

setupURLS() {
    export api_server='http://localhost:5000'
    export username='test'
    export password='test'
}

setupAccessToken() {
    export TKN=$(curl -X POST $api_server'/auth/login' \
    -H "Content-Type: application/json" \
    -X "POST" \
    -d '{"username": "'$username'","password": "'$password'"}' | jq -r '.access_token')
}

GetFees() {
    echo "*** Get fees ***"

    curl -X GET $api_server'/fees' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

GetEventTypes() {
    echo "*** Get event_types ***"

    curl -X GET $api_server'/event_types' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

Logout() {
    echo "*** Logout ***"

    curl -X POST $api_server'/auth/logout' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

# setup 
setupURLS
setupAccessToken

# API calls
GetFees
GetEventTypes
Logout
GetFees
