post_import_marketing_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for importing marketing",
    "type": "object",
    "properties": {
        "id": {"format": "number", "type": "string"},
        "marketingtxt": {"type": "string"},
        "ordernum": {"format": "number", "type": "string"},
        "visible": {"format": "number", "type": "string"}
    },
    "required": ["id", "marketingtxt", "ordernum", "visible"]
}


post_import_marketings_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema for importing marketings",
    "type": "array",
    "items": {
        "type": "object",
        "$ref": "#/definitions/marketing"
    },
    "definitions": {
        "marketing": post_import_marketing_schema
    }
}
