from maintain_api import main
from flask_testing import TestCase
from flask import url_for
from mock import patch
from unittest.mock import MagicMock


class TestStatutoryProvisions(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_get_all_statutory_provisions(self, mock_stat_provs, mock_validate):
        mock_stat_prov = MagicMock()
        mock_stat_prov.title = "abc"

        mock_stat_provs.query \
            .distinct.return_value \
            .order_by.return_value \
            .all.return_value = [mock_stat_prov]

        response = self.client.get(url_for('statutory_provisions.get_all_statutory_provisions'),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertIn("abc", response.json)
        self.assertStatus(response, 200)
        mock_validate.assert_called()
        mock_stat_provs.query.distinct.return_value.filter.return_value.order_by.return_value.all.assert_not_called()
        mock_stat_provs.query.distinct.return_value.order_by.return_value.all.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_get_filtered_statutory_provisions(self, mock_stat_provs, mock_validate):
        mock_stat_prov = MagicMock()
        mock_stat_prov.title = "abc"

        mock_stat_provs.query \
            .distinct.return_value \
            .filter.return_value \
            .order_by.return_value \
            .all.return_value = [mock_stat_prov]

        response = self.client.get(url_for('statutory_provisions.get_all_statutory_provisions', selectable=True),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertIn("abc", response.json)
        self.assertStatus(response, 200)
        mock_validate.assert_called()
        mock_stat_provs.query.distinct.return_value.filter.return_value.order_by.return_value.all.assert_called()
        mock_stat_provs.query.distinct.return_value.order_by.return_value.all.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_no_statutory_provisions(self, mock_stat_provs, mock_validate):

        mock_stat_provs.query \
            .distinct.return_value \
            .order_by.return_value \
            .all.return_value = []

        response = self.client.get(url_for('statutory_provisions.get_all_statutory_provisions'),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        self.assertIn("error_message", response.json)
        self.assertEqual('No provisions found.', response.json["error_message"])
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_add_statutory_provisions_ok(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .all.return_value = []

        response = self.client.post(url_for('statutory_provisions.add_statutory_provisions'),
                                    data='{"title":"abc", "selectable": false}',
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 201)
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_add_statutory_provisions_400(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .all.return_value = [MagicMock()]

        response = self.client.post(url_for('statutory_provisions.add_statutory_provisions'),
                                    data='{"title":"abc"}',
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)
        mock_db.session.add.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_add_statutory_provisions_409(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .all.return_value = [MagicMock()]

        response = self.client.post(url_for('statutory_provisions.add_statutory_provisions'),
                                    data='{"title":"abc", "selectable": false}',
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)
        mock_db.session.add.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_delete_statutory_provisions_ok(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .first.return_value = MagicMock()

        response = self.client.delete(url_for('statutory_provisions.delete_statutory_provisions', stat_prov="abc"),
                                      data='{"title":"abc", "selectable": false}',
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_stat_provs.query.filter.return_value.delete.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_delete_statutory_provisions_404(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .first.return_value = None

        response = self.client.delete(url_for('statutory_provisions.delete_statutory_provisions', stat_prov="abc"),
                                      data='{"title":"abc", "selectable": false}',
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_stat_provs.query.filter.return_value.delete.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_update_statutory_provisions_ok(self, mock_stat_provs, mock_db, mock_validate):
        mock_stat_prov = MagicMock()
        mock_stat_prov.title = "test"
        mock_stat_prov.selectable = False

        mock_stat_provs.query \
            .filter.return_value \
            .first.return_value = mock_stat_prov

        response = self.client.put(url_for('statutory_provisions.update_statutory_provisions', stat_prov="test"),
                                   data='{"title":"test", "selectable": false}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_update_instruments_400(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .first.return_value = None

        response = self.client.put(url_for('statutory_provisions.update_statutory_provisions', stat_prov="abc"),
                                   data='{"selectable": false}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_update_instruments_404(self, mock_stat_provs, mock_db, mock_validate):

        mock_stat_provs.query \
            .filter.return_value \
            .first.return_value = None

        response = self.client.put(url_for('statutory_provisions.update_statutory_provisions', stat_prov="abc"),
                                   data='{"title":"abc", "selectable": false}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.statutory_provisions.db')
    @patch('maintain_api.views.v1_0.statutory_provisions.StatutoryProvision')
    def test_update_instruments_409(self, mock_stat_provs, mock_db, mock_validate):
        mock_stat_prov = MagicMock()
        mock_stat_prov.title = "test"
        mock_stat_prov.selectable = False

        mock_stat_provs.query \
            .filter.return_value \
            .first.return_value = mock_stat_prov

        response = self.client.put(url_for('statutory_provisions.update_statutory_provisions', stat_prov="test"),
                                   data='{"title":"abc", "selectable": false}',
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()
