from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)
import json

from flask_jwt_extended import jwt_required

from app.dao.members_dao import (
    dao_create_member,
    dao_get_member_by_id,
)

from app.errors import register_errors

from app.models import Marketing, Member
from app.routes.members.schemas import post_import_members_schema
from app.schema_validation import validate

members_blueprint = Blueprint('members', __name__)
register_errors(members_blueprint)


@members_blueprint.route('/members/import', methods=['POST'])
@jwt_required
def import_members():
    text = request.get_data(as_text=True)
    text = text.replace('"EmailAdd": "anon"', '"EmailAdd": null')
    text = text.replace('"EmailAdd": ""', '"EmailAdd": null')
    text = text.replace('"CreationDate": "0000-00-00"', '"CreationDate": null')
    data = json.loads(text)

    validate(data, post_import_members_schema)

    errors = []
    members = []
    for item in data:
        err = ''
        member = Member.query.filter(Member.old_id == item['id']).first()

        if member:
            err = u'member already exists: {}'.format(member.old_id)
            current_app.logger.info(err)
            errors.append(err)
        else:
            member = Member(
                old_id=item['id'],
                name=item['Name'],
                email=item['EmailAdd'],
                active=item["Active"] == "y",
                created_at=item["CreationDate"],
                old_marketing_id=item["Marketing"],
                is_course_member=item["IsMember"],
                last_updated=item["LastUpdated"]
            )

            marketing = Marketing.query.filter(Marketing.old_id == item['Marketing']).first()
            if not marketing:
                err = "Cannot find marketing: {}".format(item['Marketing'])
                current_app.logger.error(err)
                errors.append(err)
                continue
            else:
                member.marketing_id = marketing.id

            dao_create_member(member)
            members.append(member)

            current_app.logger.info('Creating member: %d, %s', member.old_id, member.name)

    res = {
        "members": [m.serialize() for m in members]
    }

    if errors:
        res['errors'] = errors

    return jsonify(res), 201 if members else 400 if errors else 200
