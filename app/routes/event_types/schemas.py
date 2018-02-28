post_create_event_type_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating event_type",
    "type": "object",
    "properties": {
        "event_type": {"type": "string"},
        "event_desc": {"type": ["string", "null"]},
        "event_filename": {"type": ["string", "null"]},
        "duration": {"type": ["integer", "null"]},
        "repeat": {"type": ["integer", "null"]},
        "repeat_interval": {"type": ["integer", "null"]},
    },
    "required": ["event_type"]
}


post_update_event_type_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for updating event_type",
    "type": "object",
    "properties": {
        "event_type": {"type": "string"},
        "event_desc": {"type": ["string", "null"]},
        "event_filename": {"type": ["string", "null"]},
        "duration": {"type": ["integer", "null"]},
        "repeat": {"type": ["integer", "null"]},
        "repeat_interval": {"type": ["integer", "null"]},
    },
}
