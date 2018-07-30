#!/bin/bash
set +e

function setupURLS {
    if [ "$1" = "dev" ]; then
        export api_server="${API_BASE_URL}/dev"
    elif [ "$1" = "preview" ]; then
        export api_server="${API_BASE_URL}/preview"
    else
        export api_server='http://localhost:5000'
    fi
    export username=$ADMIN_CLIENT_ID
    export password=$ADMIN_CLIENT_SECRET

    echo "*** running on - " $api_server
}

function setupAccessToken {
    export TKN=$(curl -X POST $api_server'/auth/login' \
    -H "Content-Type: application/json" \
    -X "POST" \
    -d '{"username": "'$username'","password": "'$password'"}' | jq -r '.access_token')
    # echo $TKN
}

function GetFees {
    echo "*** Get fees ***"

    curl -X GET $api_server'/fees' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

function GetEventTypes {
    echo "*** Get event_types ***"

    curl -X GET $api_server'/event_types' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN"
}

function GetSpeakers {
    echo "*** Get speakers ***"

    curl -X GET $api_server'/speakers' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

speakers=$(cat  << EOF
    [ 
        {"title": "Mrs", "name": "Sabine Leitner", "alternate_names": "Sabine Leitner, Director of New Acropolis UK"},
        {"title": "Mr", "name": "Julian Scott"},
        {"title": "Mr", "name": "James Chan", "alternate_names": "James Chan Lee"}
    ]
EOF
)



function PostSpeakers {
    echo "*** Post speakers ***"

    curl -X POST $api_server'/speakers' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" \
    -d "$speakers"
}

    # [ 
    #     {"title": "Mrs", "name": "Sabine Leitner", "alternate_names": "Sabine Leitner, Director of New Acropolis UK"},
    #     {"title": "Mr", "name": "Julian Scott"},
    #     {"title": "Mr", "name": "James Chan", "alternate_names": "James Chan Lee"}
    # ]


function GetVenues {
    echo "*** Get venues ***"

    curl -X GET $api_server'/venues' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}


venues=$(cat  << EOF
    [
        {
            "id": "1",
            "name": "",
            "address": "19 Compton Terrace N1 2UN, next door to Union Chapel.",
            "tube": "Highbury & Islington (Victoria Line), 2 minutes walk",
            "bus": "Bus routes 4, 19, 30, 43 & 277 stop nearby"
        },
        {
            "id": "2",
            "name": "Bristol",
            "address": "Caf\u00e9 Revival, 56 Corn Street, Bristol, BS1 1JG",
            "tube": "",
            "bus": ""
        },
        {
            "id": "3",
            "name": "Bristol",
            "address": "Hamilton House, 80 Stokes Croft, Bristol, BS1 3QY",
            "tube": "",
            "bus": ""
        }
    ]
EOF
)


function ImportVenues {
    echo "*** Import venues ***"

    curl -X POST $api_server'/venues/import' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" \
    -d "$venues"
}


function Logout {
    echo "*** Logout ***"

    curl -X DELETE $api_server'/auth/logout' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

# API calls
# GetFees
# GetEventTypes
# PostSpeakers
# GetSpeakers
# ImportVenues
# GetVenues
# Logout
# GetFees

# setup 
setupURLS "$1"
setupAccessToken

case "$1" in

        -a) echo "Run all"
            GetFees
            GetEventTypes
            PostSpeakers
            GetSpeakers
            ImportVenues
            GetVenues
            Logout
            GetFees
        ;;

        -i)
                ImportVenues
        ;;

esac
