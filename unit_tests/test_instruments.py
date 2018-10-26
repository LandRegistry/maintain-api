from maintain_api import main
from flask_testing import TestCase
from flask import url_for
from mock import patch
from unittest.mock import MagicMock


class TestInstruments(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_get_all_instruments(self, mock_instruments, mock_validate):
        mock_instrument = MagicMock()
        mock_instrument.name = "abc"

        mock_instruments.query \
            .distinct.return_value \
            .order_by.return_value \
            .all.return_value = [mock_instrument]

        response = self.client.get(url_for('instruments.get_all_instruments'),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertIn("abc", response.json)
        self.assertStatus(response, 200)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_no_instruments(self, mock_instruments, mock_validate):

        mock_instruments.query \
            .distinct.return_value \
            .order_by.return_value \
            .all.return_value = []

        response = self.client.get(url_for('instruments.get_all_instruments'),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        self.assertIn("error_message", response.json)
        self.assertEqual('No instruments found.', response.json["error_message"])
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_add_instruments_ok(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .all.return_value = []

        response = self.client.post(url_for('instruments.add_instrument'),
                                    data='{"name":"abc"}',
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 201)
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_add_instruments_400(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .all.return_value = [MagicMock()]

        response = self.client.post(url_for('instruments.add_instrument'),
                                    data='{"test":"abc"}',
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)
        mock_db.session.add.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_add_instruments_409(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .all.return_value = [MagicMock()]

        response = self.client.post(url_for('instruments.add_instrument'),
                                    data='{"name":"abc"}',
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)
        mock_db.session.add.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_delete_instruments_ok(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .first.return_value = MagicMock()

        response = self.client.delete(url_for('instruments.delete_instrument', instrument_name="abc"),
                                      data='{"name":"abc"}',
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_instruments.query.filter.return_value.delete.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_delete_instruments_404(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .first.return_value = None

        response = self.client.delete(url_for('instruments.delete_instrument', instrument_name="abc"),
                                      data='{"name":"abc"}',
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_instruments.query.filter.return_value.delete.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_update_instruments_ok(self, mock_instruments, mock_db, mock_validate):
        mock_instrument = MagicMock()
        mock_instrument.name = "test"

        mock_instruments.query \
            .filter.return_value \
            .first.return_value = mock_instrument

        response = self.client.put(url_for('instruments.update_instrument', instrument_name="test"),
                                   data='{"name":"test"}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_update_instruments_400(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .first.return_value = None

        response = self.client.put(url_for('instruments.update_instrument', instrument_name="abc"),
                                   data='{"test":"abc"}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_update_instruments_404(self, mock_instruments, mock_db, mock_validate):

        mock_instruments.query \
            .filter.return_value \
            .first.return_value = None

        response = self.client.put(url_for('instruments.update_instrument', instrument_name="abc"),
                                   data='{"name":"abc"}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.instruments.db')
    @patch('maintain_api.views.v1_0.instruments.Instruments')
    def test_update_instruments_409(self, mock_instruments, mock_db, mock_validate):
        mock_instrument = MagicMock()
        mock_instrument.name = "test"

        mock_instruments.query \
            .filter.return_value \
            .first.return_value = mock_instrument

        response = self.client.put(url_for('instruments.update_instrument', instrument_name="test"),
                                   data='{"name":"abc"}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()
