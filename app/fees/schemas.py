post_create_fee_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for creating fee",
    "type": "object",
    "properties": {
        "fee": {"type": "integer"},
        "conc_fee": {"type": "integer"},
        "multi_day_fee": {"type": ["integer", "null"]},
        "multi_day_conc_fee": {"type": ["integer", "null"]},
        "valid_from": {"type": ["string", "null"], "format": "datetime"}
    },
    "required": ["fee", "conc_fee"]
}
