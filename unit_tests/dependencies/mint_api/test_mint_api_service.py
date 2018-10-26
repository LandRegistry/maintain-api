from flask import g
from unittest import TestCase
from unittest.mock import patch, MagicMock
from maintain_api.main import app
from maintain_api.dependencies.mint_api.mint_api_service import MintApiService

MINT_API_PATH = 'maintain_api.dependencies.mint_api.mint_api_service'
RESPONSE_SUCCESS = {
    "entry_number": 1,
    "local-land-charge": 2
}


class TestMintApi(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_add_to_register_success(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "123"
            response = MagicMock()
            response.status_code = 202
            response.json.return_value = RESPONSE_SUCCESS
            g.requests.post.return_value = response

            response, status = MintApiService.add_to_register({})

            self.assertTrue('entry_number' in response)
            self.assertEqual(status, 202)

    @patch('{}.current_app'.format(MINT_API_PATH))
    def test_add_to_register_exception(self, mock_current_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "123"
            response = MagicMock()
            response.status_code = 500

            ex = Exception('test exception')

            g.requests.post.side_effect = ex

            try:
                response = MintApiService.add_to_register({})
            except Exception as e:
                self.assertEqual(e.http_code, 500)
                mock_current_app.logger.exception.assert_called()
                mock_current_app.logger.exception.assert_called_with(
                    'Failed to send land charge to mint-api. Exception - test exception')

    @patch('{}.current_app'.format(MINT_API_PATH))
    def test_add_to_register_400_error_response(self, mock_current_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "123"
            response = MagicMock()
            response.status_code = 400
            response.text = 'Test error'
            response.json.return_value = RESPONSE_SUCCESS
            g.requests.post.return_value = response

            try:
                response = MintApiService.add_to_register({})
            except Exception as ex:
                self.assertEqual(ex.http_code, 400)
                mock_current_app.logger.error.assert_called()
                mock_current_app.logger.error.assert_called_with(
                    "Failed to send land charge to mint-api. Status '400', Message 'Test error'")

    @patch('{}.current_app'.format(MINT_API_PATH))
    def test_add_to_register_500_error_response(self, mock_current_app):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = "123"
            response = MagicMock()
            response.status_code = 500
            response.text = 'Test error'
            response.json.return_value = RESPONSE_SUCCESS
            g.requests.post.return_value = response

            try:
                response = MintApiService.add_to_register({})
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
                mock_current_app.logger.error.assert_called()
                mock_current_app.logger.error.assert_called_with(
                    "Failed to send land charge to mint-api. Status '500', Message 'Test error'")
