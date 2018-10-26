from unittest import TestCase
from unittest.mock import patch
from maintain_api.main import app
import json
from maintain_api.exceptions import ApplicationError

ADD_LAND_CHARGE_PATH = 'maintain_api.views.v1_0.add_land_charge'
RESPONSE_SUCCESS = {
    "entry_number": 1,
    "local-land-charge": 2
}


class TestAddLandCharge(TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.jwt_patcher = patch("maintain_api.app.validate")
        self.mock_jwt_validate = self.jwt_patcher.start()

    def tearDown(self):
        self.jwt_patcher.stop()

    @patch('{}.current_app'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.request'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.MintApiService'.format(ADD_LAND_CHARGE_PATH))
    def test_add_charge_success_with_registration_date(
        self, mock_mint_api_service, mock_request, mock_current_app
    ):
        request_data = '{"further-information-location": "123 main street","further-information-reference": "123",' \
                       '"expiry-date": "2020-01-01","charge-creation-date": "2017-01-01",' \
                       '"charge-geographic-description": "More information about ' \
                       'location","geometry": {"features": [{"geometry": {"coordinates": [[[' \
                       '606371.1076853184,284813.8509437054],[544515.2768183555,217914.9341522617],' \
                       '[520410.0576399995,287147.0361743166],[606371.1076853184,284813.8509437054]]],' \
                       '"type": "Polygon"},"properties": {"id": 1},"type": "Feature"}],"type": "FeatureCollection"},' \
                       '"statutory-provision": "Building Act 1984 section 107","charge_reason": "deed",' \
                       '"originating-authority": "City of London", "registration-date": "2012-12-12"} '

        mock_request.get_json.return_value = json.loads(request_data)
        mock_mint_api_service.add_to_register.return_value = RESPONSE_SUCCESS, 202

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        result = self.app.post('/v1.0/maintain/local-land-charge', data=request_data, headers=headers)

        self.assertEqual(result.status_code, 202)
        mock_current_app.logger.performance_platform.assert_called_with(
            "New charge successfully added. Charge ID: '2'"
        )

        # For some reason, there is no .json() function associated to
        # mocked out response, so we have to rebuild json manually ;_;
        result_json = json.loads(result.data.decode('utf-8'))

        self.assertEqual(result_json["entry_number"], 1)
        self.assertTrue("land_charge_id" in result_json)
        self.assertTrue("registration_date" in result_json)

    @patch('{}.current_app'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.request'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.MintApiService'.format(ADD_LAND_CHARGE_PATH))
    def test_add_charge_success_no_registration_date(
        self, mock_mint_api_service, mock_request, mock_current_app
    ):

        request_data = '{"further-information-location": "123 main street","further-information-reference": "123",' \
                       '"expiry-date": "2020-01-01","charge-creation-date": "2017-01-01",' \
                       '"charge-geographic-description": "More information about ' \
                       'location","geometry": {"features": [{"geometry": {"coordinates": [[[' \
                       '606371.1076853184,284813.8509437054],[544515.2768183555,217914.9341522617],' \
                       '[520410.0576399995,287147.0361743166],[606371.1076853184,284813.8509437054]]],' \
                       '"type": "Polygon"},"properties": {"id": 1},"type": "Feature"}],"type": "FeatureCollection"},' \
                       '"statutory-provision": "Building Act 1984 section 107","charge_reason": "deed",' \
                       '"originating-authority": "City of London"} '

        mock_request.get_json.return_value = json.loads(request_data)
        mock_mint_api_service.add_to_register.return_value = RESPONSE_SUCCESS, 202

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        result = self.app.post('/v1.0/maintain/local-land-charge', data=request_data, headers=headers)

        self.assertEqual(result.status_code, 202)
        mock_current_app.logger.performance_platform.assert_called_with(
            "New charge successfully added. Charge ID: '2'"
        )

        # For some reason, there is no .json() function associated to
        # mocked out response, so we have to rebuild json manually ;_;
        result_json = json.loads(result.data.decode('utf-8'))
        self.assertEqual(result_json["entry_number"], 1)
        self.assertTrue("land_charge_id" in result_json)
        self.assertTrue("registration_date" in result_json)

    @patch('{}.current_app'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.request'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.MintApiService'.format(ADD_LAND_CHARGE_PATH))
    def test_add_charge_failed(self, mock_mint_api_service, mock_request, mock_current_app):

        request_data = '{"further-information-location": "123 main street","further-information-reference": "123",' \
                       '"expiry-date": "2020-01-01","charge-creation-date": "2017-01-01",' \
                       '"charge-geographic-description": "More information about ' \
                       'location","geometry": {"features": [{"geometry": {"coordinates": [[[' \
                       '606371.1076853184,284813.8509437054],[544515.2768183555,217914.9341522617],' \
                       '[520410.0576399995,287147.0361743166],[606371.1076853184,284813.8509437054]]],' \
                       '"type": "Polygon"},"properties": {"id": 1},"type": "Feature"}],"type": "FeatureCollection"},' \
                       '"statutory-provision": "Building Act 1984 section 107","charge_reason": "deed",' \
                       '"originating-authority": "City of London", "registration-date": "2012-12-12"} '

        mock_request.get_json.return_value = json.loads(request_data)
        mock_mint_api_service.add_to_register.side_effect = Exception("test")

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        result = self.app.post('/v1.0/maintain/local-land-charge', data=request_data, headers=headers)

        self.assertEqual(result.status_code, 500)
        self.assertEqual(mock_current_app.logger.performance_platform.mock_calls, [])

    @patch('{}.current_app'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.request'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.MintApiService'.format(ADD_LAND_CHARGE_PATH))
    def test_add_charge_failed_application_error_500(self, mock_mint_api_service, mock_request, mock_current_app):

        request_data = '{"further-information-location": "123 main street","further-information-reference": "123",' \
                       '"expiry-date": "2020-01-01","charge-creation-date": "2017-01-01",' \
                       '"charge-geographic-description": "More information about ' \
                       'location","geometry": {"features": [{"geometry": {"coordinates": [[[' \
                       '606371.1076853184,284813.8509437054],[544515.2768183555,217914.9341522617],' \
                       '[520410.0576399995,287147.0361743166],[606371.1076853184,284813.8509437054]]],' \
                       '"type": "Polygon"},"properties": {"id": 1},"type": "Feature"}],"type": "FeatureCollection"},' \
                       '"statutory-provision": "Building Act 1984 section 107","charge_reason": "deed",' \
                       '"originating-authority": "City of London", "registration-date": "2012-12-12"} '

        mock_request.get_json.return_value = json.loads(request_data)
        mock_mint_api_service.add_to_register.side_effect = ApplicationError("test", "test", 500)

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        result = self.app.post('/v1.0/maintain/local-land-charge', data=request_data, headers=headers)

        self.assertEqual(result.status_code, 500)
        self.assertEqual(mock_current_app.logger.performance_platform.mock_calls, [])

    @patch('{}.current_app'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.request'.format(ADD_LAND_CHARGE_PATH))
    @patch('{}.MintApiService'.format(ADD_LAND_CHARGE_PATH))
    def test_add_charge_failed_application_error_400(self, mock_mint_api_service, mock_request, mock_current_app):

        request_data = '{"further-information-location": "123 main street","further-information-reference": "123",' \
                       '"expiry-date": "2020-01-01","charge-creation-date": "2017-01-01",' \
                       '"charge-geographic-description": "More information about ' \
                       'location","geometry": {"features": [{"geometry": {"coordinates": [[[' \
                       '606371.1076853184,284813.8509437054],[544515.2768183555,217914.9341522617],' \
                       '[520410.0576399995,287147.0361743166],[606371.1076853184,284813.8509437054]]],' \
                       '"type": "Polygon"},"properties": {"id": 1},"type": "Feature"}],"type": "FeatureCollection"},' \
                       '"statutory-provision": "Building Act 1984 section 107","charge_reason": "deed",' \
                       '"originating-authority": "City of London", "registration-date": "2012-12-12"} '

        mock_request.get_json.return_value = json.loads(request_data)
        mock_mint_api_service.add_to_register.side_effect = \
            ApplicationError('Invalid request. For more information check the logs for TraceID', "test", 400)

        headers = {'Content-Type': 'application/json', 'Authorization': 'NOTAREALJWT'}
        result = self.app.post('/v1.0/maintain/local-land-charge', data=request_data, headers=headers)

        self.assertEqual(result.status_code, 400)
        self.assertIn('Invalid request. For more information check the logs for TraceID', result.data.decode())
        self.assertEqual(mock_current_app.logger.performance_platform.mock_calls, [])
