from app.schema_validation.definitions import uuid


post_create_speaker_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating speaker",
    "type": "object",
    "properties": {
        'title': {"type": "string"},
        'name': {"type": "string"},
    },
    "required": ["name"]
}

post_create_speakers_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating speakers",
    "type": "array",
    "items": {
        "type": "object",
        "$ref": "#/definitions/speaker"
    },
    "definitions": {
        "speaker": post_create_speaker_schema
    }
}

post_update_speaker_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for updating speaker",
    "type": "object",
    "properties": {
        'title': {"type": "string"},
        'name': {"type": "string"},
    },
}
