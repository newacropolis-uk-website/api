post_login_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "POST schema login",
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"},
    },
    "required": ["username", "password"]
}
