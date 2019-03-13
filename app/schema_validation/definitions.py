uuid = {
    "type": "string",
    "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
    "validationMessage": "is not a valid UUID",
}

datetime = {
    "type": "string",
    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}(:[0-9]{2})?$",
    "validationMessage": "is not a datetime in format YYYY-MM-DD HH:MM(:SS)?",
}

number = {
    "type": "string",
    "pattern": "^[0-9]+$",
    "validationMessage": "is not a number",
}


def nullable(schema_type):
    return {
        "oneOf": [
            {"type": "null"},
            {
                "format": schema_type,
                "type": "string"
            }
        ]
    }  # pragma: no cover
