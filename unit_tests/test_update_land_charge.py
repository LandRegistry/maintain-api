from unittest import TestCase
from unittest.mock import patch, MagicMock
from maintain_api.main import app

import json

RESPONSE_SUCCESS = {
    "entry_number": 1,
    "local-land-charge": 2
}


class TestUpdateLandCharge(TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.jwt_patcher = patch("maintain_api.app.validate")
        self.mock_jwt_validate = self.jwt_patcher.start()

    def tearDown(self):
        self.jwt_patcher.stop()

    @patch('maintain_api.views.v1_0.update_land_charge.current_app')
    @patch('maintain_api.views.v1_0.update_land_charge.MintApiService')
    @patch('maintain_api.views.v1_0.update_land_charge.SearchApiService')
    def test_update_charge(self, mock_search_api_service, mock_mint_api_service, mock_current_app):

        response = MagicMock()
        response.status_code = 200
        mock_search_api_service.get_by_charge_number.return_value = response
        mock_mint_api_service.add_to_register.return_value = RESPONSE_SUCCESS, 202

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        payload_json = {"local-land-charge": 123, "registration-date": "2012-10-10"}
        result = self.app.put('/v1.0/maintain/local-land-charge/123', data=json.dumps(payload_json), headers=headers)
        mock_current_app.logger.performance_platform.assert_called_with(
            "Successfully updated charge '123'"
        )
        result_json = json.loads(result.data.decode('utf-8'))
        self.assertEqual(result.status_code, 202)
        self.assertEqual(result_json, {'entry_number': 1, 'land_charge_id': 2, 'registration_date': '2012-10-10'})

    @patch('maintain_api.views.v1_0.update_land_charge.current_app')
    @patch('maintain_api.views.v1_0.update_land_charge.MintApiService')
    @patch('maintain_api.views.v1_0.update_land_charge.SearchApiService')
    def test_cancel_charge(self, mock_search_api_service, mock_mint_api_service, mock_current_app):

        response = MagicMock()
        response.status_code = 200
        mock_search_api_service.get_by_charge_number.return_value = response
        mock_mint_api_service.add_to_register.return_value = RESPONSE_SUCCESS, 202

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        payload_json = {"local-land-charge": 123, "registration-date": "2012-10-10", "end-date": "2020-10-10"}
        result = self.app.put('/v1.0/maintain/local-land-charge/123', data=json.dumps(payload_json), headers=headers)
        mock_current_app.logger.performance_platform.assert_called_with(
            "Successfully cancelled charge '123'"
        )
        result_json = json.loads(result.data.decode('utf-8'))
        self.assertEqual(result.status_code, 202)
        self.assertEqual(result_json, {'entry_number': 1, 'land_charge_id': 2, 'registration_date': '2012-10-10'})

    @patch('maintain_api.views.v1_0.update_land_charge.current_app')
    def test_update_charge_nomatch(self, mock_current_app):
        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        payload_json = {"local-land-charge": 123, "registration-date": "2012-10-10"}
        result = self.app.put('/v1.0/maintain/local-land-charge/1234', data=json.dumps(payload_json), headers=headers)
        self.assertEqual(mock_current_app.logger.performance_platform.mock_calls, [])
        result_json = json.loads(result.data.decode('utf-8'))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result_json, {'error_code': 'U100',
                                       'error_message': 'Cannot change local-land-charge field'})

    @patch('maintain_api.views.v1_0.update_land_charge.current_app')
    @patch('maintain_api.views.v1_0.update_land_charge.SearchApiService')
    def test_charge_not_found(self, mock_search_api_service, mock_current_app):

        response = MagicMock()
        response.status_code = 404
        mock_search_api_service.get_by_charge_number.return_value = response

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        payload_json = {"local-land-charge": 123, "registration-date": "2012-10-10"}
        result = self.app.put('/v1.0/maintain/local-land-charge/123', data=json.dumps(payload_json), headers=headers)

        self.assertEqual(mock_current_app.logger.performance_platform.mock_calls, [])
        result_json = json.loads(result.data.decode('utf-8'))
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result_json, {'error_code': 'U101',
                                       'error_message': 'Cannot find local land charge'})
