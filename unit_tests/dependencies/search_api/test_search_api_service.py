from flask import g
from unittest import TestCase
from unittest.mock import MagicMock
from maintain_api.main import app
from maintain_api.dependencies.search_api.search_api_service import SearchApiService

SEARCH_API_PATH = 'maintain_api.dependencies.search_api.search_api_service'


class TestSearchApi(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_charge(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "123"
            charge_no = "123"
            response = MagicMock()
            response.status_code = 200
            g.requests.get.return_value = response

            response = SearchApiService.get_by_charge_number(charge_no)

            self.assertEqual(response.status_code, 200)
