import unittest
from mock import patch
from maintain_api.main import app


class TestCustomLogLevel(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @patch('maintain_api.main.app.logger.performance_platform')
    def test_performance_platform_log_level(self, performance_platform_logging_level_mock):
        app.logger.performance_platform('test')

        performance_platform_logging_level_mock.assert_called_with('test')
