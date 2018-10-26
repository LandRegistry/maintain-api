from flask import current_app, g
from maintain_api.config import MINT_API_URL
from maintain_api.exceptions import ApplicationError
from maintain_api.utilities.charge_id import encode_charge_id


class MintApiService(object):
    @staticmethod
    def add_to_register(add_land_charge_data):
        try:
            response = g.requests.post(MINT_API_URL, data=add_land_charge_data,
                                       headers={'Content-Type': 'application/json'})
        except Exception as ex:
            error_message = 'Failed to send land charge to mint-api. Exception - {}'.format(ex)
            current_app.logger.exception(error_message)
            raise ApplicationError(error_message, 'ADD_TO_REGISTER')

        if response.status_code != 202:
            error_message = "Failed to send land charge to mint-api. Status '{}', Message '{}'"\
                .format(response.status_code, response.text)
            current_app.logger.error(error_message)
            if response.status_code != 400:
                raise ApplicationError(error_message, 'ADD_TO_REGISTER')
            result = response.json()
        else:
            result = response.json()
            result['local-land-charge'] = encode_charge_id(result['local-land-charge'])
            current_app.audit_logger.info("New charge created. entry number: {}".format(result['entry_number']))

        return result, response.status_code
