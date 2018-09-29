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
    echo $TKN
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

event_types=$(cat  << EOF
    [
        {"id":"1","EventType":"Talk","Fees":"5","ConcFees":"3","EventDesc":"","EventFilename":null},
        {"id":"2","EventType":"Introductory Course","Fees":"120","ConcFees":"85","EventDesc":"","EventFilename":null},
        {"id":"3","EventType":"Seminar","Fees":"0","ConcFees":null,"EventDesc":"","EventFilename":null},
        {"id":"4","EventType":"Ecological event","Fees":"0","ConcFees":null,"EventDesc":"","EventFilename":null},
        {"id":"5","EventType":"Excursion","Fees":"0","ConcFees":null,"EventDesc":"","EventFilename":"TextExcursion.gif"},
        {"id":"6","EventType":"Exhibition","Fees":"0","ConcFees":null,"EventDesc":"","EventFilename":null},
        {"id":"7","EventType":"Meeting","Fees":"0","ConcFees":null,"EventDesc":"","EventFilename":null},
        {"id":"8","EventType":"Cultural Event","Fees":"0","ConcFees":null,"EventDesc":"","EventFilename":"TextCultural.gif"},
        {"id":"9","EventType":"Short Course","Fees":"0","ConcFees":null,"EventDesc":null,"EventFilename":null},
        {"id":"10","EventType":"Workshop","Fees":"0","ConcFees":null,"EventDesc":null,"EventFilename":null}
    ]
EOF
)

function ImportEventTypes {
    echo "*** Import event types ***"

    curl -X POST $api_server'/event_types/import' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" \
    -d "$event_types"
}

function GetSpeakers {
    echo "*** Get speakers ***"

    curl -X GET $api_server'/speakers' \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TKN" | jq .
}

# speakers=$(cat  << EOF
#     [ 
#         {"title": "Mrs", "name": "Sabine Leitner", "alternate_names": "Sabine Leitner, Director of New Acropolis UK"},
#         {"title": "Mr", "name": "Julian Scott"},
#         {"title": "Mr", "name": "James Chan", "alternate_names": "James Chan Lee"}
#     ]
# EOF
# )

speakers=$(cat  << EOF
    [ 
        {"title": "Mrs", "name": "Sabine Leitner"},
        {"name": "Sabine Leitner, Director of New Acropolis UK", "parent_name": "Sabine Leitner"},
        {"title": "Mr", "name": "Julian Scott"},
        {"title": "Mr", "name": "James Chan"},
        {"name": "James Chan Lee", "parent_name": "James Chan"}
    ]
EOF
)

function ImportSpeakers {
    echo "*** Import speakers ***"

    curl -X POST $api_server'/speakers/import' \
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
setupURLS "$2"
setupAccessToken

if [ -z $1 ]; then
    arg="-a"
else
    arg=$1
fi

case "$arg" in

        -a) echo "Run all"
            GetFees
            GetEventTypes
            ImportEventTypes
            ImportSpeakers
            GetSpeakers
            ImportVenues
            GetVenues
            Logout
            GetFees
        ;;

        -et)
            GetEventTypes
        ;;

        -iet)
            ImportEventTypes
        ;;

        -i)
            ImportVenues
        ;;

        -s)
            GetSpeakers
        ;;

        -is)
            ImportSpeakers
        ;;

        -x)
            Logout
        ;;

esac
