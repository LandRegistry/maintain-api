from flask import Blueprint, Response, current_app, request
from maintain_api.models import StatutoryProvision
from maintain_api.exceptions import ApplicationError
from sqlalchemy import func
import json
from maintain_api.extensions import db
from jsonschema import validate, ValidationError

statutory_provision_bp = Blueprint('statutory_provisions', __name__, url_prefix='/statutory-provisions')


STAT_PROV_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "selectable": {"type": "boolean"}
    },
    "additionalProperties": False,
    "required": ["title", "selectable"]
}


@statutory_provision_bp.route('/statutory-provisions', methods=['GET'])
def get_all_statutory_provisions():
    current_app.logger.info("Get all statutory provisions.")

    selectable = request.args.get('selectable')

    if selectable is None:
        provisions = StatutoryProvision.query \
            .distinct(StatutoryProvision.title) \
            .order_by(StatutoryProvision.title) \
            .all()
    else:
        provisions = StatutoryProvision.query \
            .distinct(StatutoryProvision.title) \
            .filter(StatutoryProvision.selectable == selectable) \
            .order_by(StatutoryProvision.title) \
            .all()

    if provisions is None or len(provisions) == 0:
        raise ApplicationError("No provisions found.", 404, 404)

    provisions_json = []
    for provision in provisions:
        provisions_json.append(provision.title)

    return Response(response=json.dumps(provisions_json), mimetype="application/json")


@statutory_provision_bp.route('/statutory-provisions', methods=['POST'])
def add_statutory_provisions():
    current_app.logger.info("Add statutory provision.")

    request_body = request.get_json()

    try:
        validate(request_body, STAT_PROV_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Add statutory provision - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    title = request_body["title"]
    selectable = request_body["selectable"]

    exists = StatutoryProvision.query.filter(func.lower(StatutoryProvision.title) == func.lower(title)).all()

    if exists is not None and len(exists) > 0:
        message = "Statutory provision '{0}' already exists.".format(title)
        current_app.logger.info(message)
        raise ApplicationError(message, 409, 409)

    stat_prov = StatutoryProvision(title, selectable)

    db.session.add(stat_prov)
    db.session.commit()

    return "", 201


@statutory_provision_bp.route('/statutory-provisions/<stat_prov>', methods=['DELETE'])
def delete_statutory_provisions(stat_prov):
    current_app.logger.info("Delete statutory provision {0}.".format(stat_prov))

    provision = StatutoryProvision.query.filter(func.lower(StatutoryProvision.title) == func.lower(stat_prov)).first()

    if provision is None:
        message = "Statutory provision '{0}' does not exist.".format(stat_prov)
        current_app.logger.info(message)
        raise ApplicationError(message, 404, 404)

    StatutoryProvision.query.filter(StatutoryProvision.id == provision.id).delete()
    db.session.commit()

    return "", 204


@statutory_provision_bp.route('/statutory-provisions/<stat_prov>', methods=['PUT'])
def update_statutory_provisions(stat_prov):
    current_app.logger.info("Update statutory provision {0}.".format(stat_prov))

    request_body = request.get_json()

    try:
        validate(request_body, STAT_PROV_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Update statutory provision - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    title = request_body["title"]
    selectable = request_body["selectable"]

    provision = StatutoryProvision.query.filter(func.lower(StatutoryProvision.title) == func.lower(stat_prov)).first()

    if provision is None:
        message = "Statutory provision '{0}' does not exist.".format(stat_prov)
        current_app.logger.info(message)
        raise ApplicationError(message, 404, 404)

    if provision.title.lower() != title.lower():
        inuse = StatutoryProvision.query.filter(func.lower(StatutoryProvision.title) == func.lower(title)).first()
        if inuse is not None:
            message = "Statutory provision with name '{0}' already exists.".format(title)
            current_app.logger.info(message)
            raise ApplicationError(message, 409, 409)

    provision.title = title
    provision.selectable = selectable
    db.session.commit()

    return "", 204
