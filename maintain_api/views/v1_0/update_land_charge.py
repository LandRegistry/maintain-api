from flask import request, Blueprint
from maintain_api.exceptions import ApplicationError
from maintain_api.dependencies.mint_api.mint_api_service import MintApiService
from maintain_api.dependencies.search_api.search_api_service import SearchApiService
from maintain_api.utilities.charge_id import encode_charge_id
from flask import current_app
import json

update_land_charge_bp = Blueprint('update_land_charge', __name__)


@update_land_charge_bp.route('/local-land-charge/<land_charge_id>', methods=['PUT'])
def update_land_charge(land_charge_id):
    """Update a land charge"""

    current_app.logger.info("Endpoint called")

    payload = request.get_json()

    if str(payload['local-land-charge']) == land_charge_id:

        encoded_charge = encode_charge_id(payload['local-land-charge'])
        response = SearchApiService.get_by_charge_number(encoded_charge)

        if response.status_code != 200:
            current_app.logger.error("Charge does not exist")
            raise ApplicationError("Cannot find local land charge", "U101", 400)

        current_app.logger.info("Sending charge to mint")

        result, status = MintApiService.add_to_register(json.dumps(payload, sort_keys=True, separators=(',', ':')))

        if status == 202:
            built_resp = {
                "entry_number": result['entry_number'],
                "land_charge_id": result['local-land-charge'],
                "registration_date": payload['registration-date']
            }

            if 'end-date' in payload and payload['end-date']:
                # Used for calculating performance platform metrics
                current_app.logger.performance_platform(
                    "Successfully cancelled charge '{}'".format(land_charge_id)
                )
            else:
                # Used for calculating performance platform metrics
                current_app.logger.performance_platform(
                    "Successfully updated charge '{}'".format(land_charge_id)
                )
        else:
            # return result from Mint api
            built_resp = result
    else:
        current_app.logger.warning("Cannot change local-land-charge field for charge '{}'".format(land_charge_id))
        raise ApplicationError("Cannot change local-land-charge field", "U100", 400)

    current_app.logger.info("Returning update response for charge '{}'".format(land_charge_id))

    return json.dumps(built_resp, sort_keys=True, separators=(',', ':')), status, {'Content-Type': 'application/json'}
