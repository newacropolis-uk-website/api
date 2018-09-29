from app.schema_validation.definitions import uuid


post_create_speaker_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating speaker",
    "type": "object",
    "properties": {
        'title': {"type": "string"},
        'name': {"type": "string"},
        'parent_id': uuid,
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
        'parent_id': uuid,
    },
}

post_import_speaker_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for importing speaker",
    "type": "object",
    "properties": {
        'title': {"type": "string"},
        'name': {"type": "string"},
        'parent_name': {"type": "string"},
    },
    "required": ["name"]
}

post_import_speakers_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for importing speakers",
    "type": "array",
    "items": {
        "type": "object",
        "$ref": "#/definitions/speaker"
    },
    "definitions": {
        "speaker": post_import_speaker_schema
    }
}
