from flask import current_app, g
from maintain_api.config import SEARCH_API_URL


class SearchApiService(object):
    """Service class for making requests to /local_land_charges endpoint"""

    @staticmethod
    def get_by_charge_number(charge_number):
        current_app.logger.info("Method called")
        url = "{}/search/local_land_charges/{}".format(SEARCH_API_URL, charge_number)
        current_app.logger.info("Calling search api via this URL: %s", url)
        return g.requests.get(url)
