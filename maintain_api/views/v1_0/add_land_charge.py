from flask import request, Blueprint, current_app
from maintain_api.dependencies.mint_api.mint_api_service import MintApiService
import json
import datetime

add_land_charge_bp = Blueprint('add_land_charge', __name__)


@add_land_charge_bp.route('/local-land-charge', methods=['POST'])
def add_charge():
    """Add a land charge"""
    current_app.logger.info("Endpoint called")
    payload = request.get_json()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    if 'registration-date' not in payload:
        payload['registration-date'] = date

    payload['start-date'] = date

    current_app.logger.info("Sending charge to mint")

    result, status = MintApiService.add_to_register(json.dumps(payload, sort_keys=True, separators=(',', ':')))

    if status == 202:
        # build response for successful call to Mint api
        current_app.logger.info("Charge sent to mint - Building response")

        built_resp = {
            "entry_number": result['entry_number'],
            "land_charge_id": result['local-land-charge'],
            "registration_date": payload['registration-date']
        }

        # Used for calculating performance platform metrics
        current_app.logger.performance_platform(
            "New charge successfully added. Charge ID: '{}'"
            .format(built_resp["land_charge_id"])
        )
    else:
        # return result from Mint api
        built_resp = result

    return json.dumps(built_resp, sort_keys=True, separators=(',', ':')), status, {'Content-Type': 'application/json'}
