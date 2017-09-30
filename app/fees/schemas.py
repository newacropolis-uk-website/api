from app.schema_validation.definitions import uuid


post_create_fee_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating fee",
    "type": "object",
    "properties": {
        "event_type_id": uuid,
        "fee": {"type": "integer"},
        "conc_fee": {"type": "integer"},
        "multi_day_fee": {"type": ["integer", "null"]},
        "multi_day_conc_fee": {"type": ["integer", "null"]},
    },
    "required": ["event_type_id", "fee", "conc_fee"]
}


post_update_fee_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for updating fee",
    "type": "object",
    "properties": {
        "event_type_id": uuid,
        "fee": {"type": "integer"},
        "conc_fee": {"type": "integer"},
        "multi_day_fee": {"type": ["integer", "null"]},
        "multi_day_conc_fee": {"type": ["integer", "null"]},
    },
}
