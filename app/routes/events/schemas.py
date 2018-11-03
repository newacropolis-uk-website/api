from app.schema_validation.definitions import uuid, datetime, number


post_create_event_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating venue",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "address": {"type": "string"},
        "directions": {"type": ["string", "null"]},
        "default": {"type": ["boolean", "false"]},
    },
    "required": ["name", "address"]
}


post_import_event_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for importing event",
    "type": "object",
    "properties": {
        "id": {
            "format": "number",
            "type": "string"
        },
        "BookingCode": {"type": "string"},
        "MemberPay": {"type": "string"},                    # unused
        "Approved": {"type": "string"},                     # unused
        "Type": {
            "format": "number",
            "type": "string"
        },
        "Title": {"type": "string"},
        "SubTitle": {"type": "string"},
        "Description": {"type": "string"},
        "venue": {
            "format": "number",
            "type": "string"
        },
        "Speaker": {"type": "string"},
        "MultiDayFee": {
            "oneOf": [
                {"type": "null"},
                {
                    "format": "number",
                    "type": "string"
                }
            ]
        },
        "MultiDayConcFee": {
            "oneOf": [
                {"type": "null"},
                {
                    "format": "number",
                    "type": "string"
                }
            ]
        },
        "StartDate": {
            "format": "date-time",
            "type": "string",
            "description": "Date+time event"
        },
        "StartDate2": {
            "format": "date-time",
            "type": ["string", "null"],
            "description": "Date+time event 2"
        },
        "StartDate3": {
            "format": "date-time",
            "type": ["string", "null"],
            "description": "Date+time event 3"
        },
        "StartDate4": {
            "format": "date-time",
            "type": ["string", "null"],
            "description": "Date+time event 4"
        },
        "EndDate": {
            "format": "date-time",
            "type": ["string", "null"],
            "description": "End date+time event"
        },
        "Duration": {
            "format": "number",
            "type": "string"
        },
        "Fee": {
            "oneOf": [
                {"type": "null"},
                {
                    "format": "number",
                    "type": "string"
                }
            ]
        },
        "ConcFee": {
            "oneOf": [
                {"type": "null"},
                {
                    "format": "number",
                    "type": "string"
                }
            ]
        },
        "Pub-First-Number": {"type": ["string", "null"]},   # unused
        "Mem-SignOn-Number": {"type": ["string", "null"]},  # unused
        "ImageFilename": {"type": "string"},
        "WebLink": {"type": "string"},                      # unused
        "LinkText": {"type": ["string", "null"]},                     # unused
        "MembersOnly": {"type": "string"},                  # unused
        "RegisterStartOnly": {"type": "string"},            # unused
        "SoldOut": {"type": ["string", "null"]},            # unused
    },
    "required": ["id", "Type", "Title"]
}

post_import_events_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for importing events",
    "type": "array",
    "items": {
        "type": "object",
        "$ref": "#/definitions/event"
    },
    "definitions": {
        "event": post_import_event_schema
    }
}

post_update_event_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for updating venue",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "address": {"type": "string"},
        "directions": {"type": ["string", "null"]},
        "default": {"type": ["boolean", "false"]},
    },
}
