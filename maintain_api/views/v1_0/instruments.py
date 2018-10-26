from flask import Blueprint, Response, current_app, request
from maintain_api.models import Instruments
from maintain_api.exceptions import ApplicationError
from sqlalchemy import func
import json
from jsonschema import validate, ValidationError
from maintain_api.extensions import db

instruments_bp = Blueprint('instruments', __name__, url_prefix='/v1.0/maintain/instruments')


INSTRUMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"}
    },
    "additionalProperties": False,
    "required": ["name"]
}


@instruments_bp.route('', methods=['GET'])
def get_all_instruments():
    current_app.logger.info("Get all instruments.")
    instruments = Instruments.query \
        .distinct(Instruments.name) \
        .order_by(Instruments.name) \
        .all()

    if instruments is None or len(instruments) == 0:
        raise ApplicationError("No instruments found.", 404, 404)

    instruments_json = []
    for instrument in instruments:
        instruments_json.append(instrument.name)

    return Response(response=json.dumps(instruments_json), mimetype="application/json")


@instruments_bp.route('', methods=['POST'])
def add_instrument():
    current_app.logger.info("Add instruments.")

    request_body = request.get_json()

    try:
        validate(request_body, INSTRUMENT_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Create instrument - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    name = request_body["name"]

    exists = Instruments.query.filter(func.lower(Instruments.name) == func.lower(name)).all()

    if exists is not None and len(exists) > 0:
        message = "Instrument '{0}' already exists.".format(name)
        current_app.logger.info(message)
        raise ApplicationError(message, 409, 409)

    instrument = Instruments(name)

    db.session.add(instrument)
    db.session.commit()

    return "", 201


@instruments_bp.route('/<instrument_name>', methods=['DELETE'])
def delete_instrument(instrument_name):
    current_app.logger.info("Delete instruments.")

    instrument = Instruments.query.filter(func.lower(Instruments.name) == func.lower(instrument_name)).first()

    if instrument is None:
        message = "Instrument '{0}' does not exist.".format(instrument_name)
        current_app.logger.info(message)
        raise ApplicationError(message, 404, 404)

    Instruments.query.filter(Instruments.id == instrument.id).delete()
    db.session.commit()

    return "", 204


@instruments_bp.route('/<instrument_name>', methods=['PUT'])
def update_instrument(instrument_name):
    current_app.logger.info("Update instrument {0}.".format(instrument_name))

    request_body = request.get_json()

    try:
        validate(request_body, INSTRUMENT_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Update instrument - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    name = request_body["name"]

    instrument = Instruments.query.filter(func.lower(Instruments.name) == func.lower(instrument_name)).first()

    if instrument is None:
        message = "Instrument '{0}' does not exist.".format(name)
        current_app.logger.info(message)
        raise ApplicationError(message, 404, 404)

    if instrument.name.lower() != name.lower():
        inuse = Instruments.query.filter(func.lower(Instruments.name) == func.lower(name)).first()
        if inuse is not None:
            message = "Instrument with name '{0}' already exists.".format(name)
            current_app.logger.info(message)
            raise ApplicationError(message, 409, 409)

    instrument.name = name
    db.session.commit()

    return "", 204
