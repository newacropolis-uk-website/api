from app.schema_validation.definitions import uuid, datetime

post_create_event_date_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating event_date",
    "type": "object",
    "properties": {
        "event_id": uuid,
        "event_datetime": datetime,
    },
    "required": ["event_id", "event_datetime"]
}


post_update_event_date_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for updating event_date",
    "type": "object",
    "properties": {
        "event_datetime": datetime,
    },
}
