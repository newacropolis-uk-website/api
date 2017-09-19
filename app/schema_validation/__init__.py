import json
from datetime import datetime, timedelta

from iso8601 import iso8601, ParseError
from jsonschema import (Draft4Validator, ValidationError, FormatChecker)


def validate(json_to_validate, schema):
    format_checker = FormatChecker()

    @format_checker.checks('datetime', raises=ValidationError)
    def validate_schema_date_with_hour(instance):
        if isinstance(instance, str) or isinstance(instance, unicode):
            try:
                dt = iso8601.parse_date(instance).replace(tzinfo=None)
            except ParseError:
                raise ValidationError("datetime format is invalid. It must be a valid ISO8601 date time format, "
                                      "https://en.wikipedia.org/wiki/ISO_8601")
        return True

    validator = Draft4Validator(schema, format_checker=format_checker)
    errors = list(validator.iter_errors(json_to_validate))
    if errors.__len__() > 0:
        raise ValidationError(build_error_message(errors))
    return json_to_validate


def build_error_message(errors):
    fields = []
    for e in errors:
        field = (
            "{} {}".format(e.path[0], e.schema['validationMessage'])
            if 'validationMessage' in e.schema else __format_message(e)
        )
        fields.append({"error": "ValidationError", "message": field})
    message = {
        "status_code": 400,
        "errors": unique_errors(fields)
    }

    return json.dumps(message)


def unique_errors(dups):
    unique = []
    for x in dups:
        if x not in unique:
            unique.append(x)
    return unique


def __format_message(e):
    def get_path(e):
        error_path = None
        try:
            error_path = e.path.popleft()
            # no need to catch IndexError exception explicity as
            # error_path is None if e.path has no items
        finally:
            return error_path

    def get_error_message(e):
        # e.cause is an exception (such as InvalidPhoneError). if it's not present it was a standard jsonschema error
        # such as a required field not being present
        error_message = str(e.cause) if e.cause else e.message
        return error_message.replace("'", '')

    path = get_path(e)
    message = get_error_message(e)
    if path:
        return "{} {}".format(path, message)
    else:
        return "{}".format(message)
