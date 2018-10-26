from maintain_api import main
from flask_testing import TestCase
from flask import url_for
from mock import patch
from unittest.mock import MagicMock
import json


class TestCategories(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_all_categories(self, mock_categories, mock_validate):
        mock_category = MagicMock()
        mock_category.name = "abc"
        mock_category.display_name = "Display"
        mock_category.permission = "test permission"

        mock_categories.query \
            .filter.return_value \
            .order_by.return_value \
            .all.return_value = [mock_category]

        response = self.client.get(url_for('categories.get_all_categories'),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)
        self.assertEqual(1, len(response.json))
        self.assertEqual("abc", response.json[0]['name'])
        self.assertEqual("Display", response.json[0]['display-name'])
        self.assertEqual("test permission", response.json[0]['permission'])
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_no_maps(self, mock_categories, mock_db,
                                  mock_provisions, mock_instruments, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": [],
                "instruments": []}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = None

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 201)

        mock_db.session.add.assert_called()
        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_with_provisions(self, mock_categories, mock_db,
                                          mock_provisions, mock_instruments, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": []}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = None

        mock_provision = MagicMock()
        mock_provision.id = 1
        mock_provisions.query.filter.return_value.first.return_value = mock_provision

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 201)

        mock_db.session.add.assert_called()
        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_with_instruments(self, mock_categories, mock_db,
                                           mock_provisions, mock_instruments, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": [],
                "instruments": ["abc"]}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = None

        mock_instrument = MagicMock()
        mock_instrument.id = 1
        mock_instruments.query.filter.return_value.first.return_value = mock_instrument

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 201)

        mock_db.session.add.assert_called()
        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_called()
        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_400(self, mock_categories, mock_db,
                              mock_provisions, mock_instruments, mock_validate):

        data = {"namess": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": [],
                "instruments": []}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = None

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)

        mock_validate.assert_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_409(self, mock_categories, mock_db,
                              mock_provisions, mock_instruments, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": [],
                "instruments": []}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = MagicMock()

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)

        mock_validate.assert_called()
        mock_db.session.add.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_instruments_does_not_exist(self, mock_categories, mock_db,
                                                     mock_provisions, mock_instruments, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": [],
                "instruments": ["abc"]}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = None

        mock_instruments.query.filter.return_value.first.return_value = None

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.add.assert_called()
        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_category_provisions_does_not_exist(self, mock_categories, mock_db,
                                                    mock_provisions, mock_instruments, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": []}

        mock_categories.query \
            .filter.return_value \
            .filter.return_value \
            .first.return_value = None

        mock_provisions.query.filter.return_value.first.return_value = None

        response = self.client.post(url_for('categories.add_categories'),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.add.assert_called()
        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_not_called()
        mock_validate.assert_called()
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_categories.query.filter.return_value.first.assert_not_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_category_no_sub_categories_or_mapping(self, mock_categories, mock_validate):

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = None
        mock_category.provisions = []
        mock_category.instruments = []

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_categories.query.filter.return_value.order_by.return_value.all.return_value = []

        response = self.client.get(url_for('categories.get_category', category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)
        self.assertEqual("abc", response.json["name"])
        self.assertEqual("display", response.json["display-name"])
        self.assertEqual("permission", response.json["permission"])
        self.assertEqual([], response.json["statutory-provisions"])
        self.assertEqual([], response.json["instruments"])
        self.assertEqual([], response.json["sub-categories"])
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_category_with_all_mapping(self, mock_categories, mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_sub_category = MagicMock()
        mock_sub_category.name = "Child"
        mock_sub_category.display_name = "child display"
        mock_sub_category.permission = "child permission"

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_categories.query.filter.return_value.order_by.return_value.all.return_value = [mock_sub_category]

        response = self.client.get(url_for('categories.get_category', category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)
        self.assertEqual("abc", response.json["name"])
        self.assertEqual("display", response.json["display-name"])
        self.assertEqual("permission", response.json["permission"])
        self.assertEqual(['abc'], response.json["statutory-provisions"])
        self.assertEqual(['def'], response.json["instruments"])
        self.assertEqual("Child", response.json["sub-categories"][0]['name'])
        self.assertEqual("child display", response.json["sub-categories"][0]['display-name'])
        self.assertEqual("child permission", response.json["sub-categories"][0]['permission'])
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_category_404(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.get(url_for('categories.get_category', category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_category_with_sub_categories(self, mock_categories, mock_db,
                                                 mock_provisions, mock_instruments, mock_validate):

        mock_category = MagicMock()
        mock_category.id = 1

        mock_sub_category1 = MagicMock()
        mock_sub_category1.id = 2

        mock_sub_category2 = MagicMock()
        mock_sub_category2.id = 3

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_categories.query\
            .filter.return_value\
            .all.return_value = [mock_sub_category1, mock_sub_category2]

        response = self.client.delete(url_for('categories.delete_category', category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)
        mock_instruments.query.filter.return_value.delete.assert_called()
        self.assertEqual(3, mock_instruments.query.filter.return_value.delete.call_count)

        mock_provisions.query.filter.return_value.delete.assert_called()
        self.assertEqual(3, mock_provisions.query.filter.return_value.delete.call_count)

        mock_categories.query.filter.return_value.delete.assert_called()
        self.assertEqual(3, mock_categories.query.filter.return_value.delete.call_count)

        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_category_with_out_sub_categories(self, mock_categories, mock_db,
                                                     mock_provisions, mock_instruments, mock_validate):

        mock_category = MagicMock()
        mock_category.id = 1

        mock_categories.query.filter.return_value.first.return_value = mock_category

        mock_categories.query \
            .filter.return_value \
            .all.return_value = []

        response = self.client.delete(url_for('categories.delete_category', category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)
        mock_instruments.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_instruments.query.filter.return_value.delete.call_count)

        mock_provisions.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_provisions.query.filter.return_value.delete.call_count)

        mock_categories.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.delete.call_count)

        mock_db.session.commit.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_category_404(self, mock_categories, mock_db, mock_provisions, mock_instruments, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.delete(url_for('categories.delete_category', category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        mock_instruments.query.filter.return_value.delete.assert_not_called()
        mock_provisions.query.filter.return_value.delete.assert_not_called()
        mock_categories.query.filter.return_value.delete.assert_not_called()
        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_db.session.rollback.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_category_no_maps(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                     mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": [],
                "instruments": []}

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "Planning"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = None
        mock_category.provisions = []
        mock_category.instruments = []

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        response = self.client.put(url_for('categories.update_category', category_name="Planning"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_db.session.commit.assert_called()
        mock_prov_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_instrument_map.query.filter.return_value.delete.call_count)
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_category_with_maps(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                       mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "Planning"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = None
        mock_category.provisions = []
        mock_category.instruments = []

        mock_stat_prov = MagicMock()
        mock_stat_prov.id = 1
        mock_instrument = MagicMock()
        mock_instrument.id = 1

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_instruments.query.filter.return_value.first.return_value = mock_instrument
        mock_provisions.query.filter.return_value.first.return_value = mock_stat_prov

        response = self.client.put(url_for('categories.update_category', category_name="Planning"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_db.session.commit.assert_called()
        mock_prov_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_instrument_map.query.filter.return_value.delete.call_count)
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_provisions.query.filter.return_value.first.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_category_400(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                 mock_prov_map, mock_instrument_map, mock_validate):

        data = {
            "display-name": "Planning",
            "display-order": 11,
            "permission": None,
            "provisions": ["abc"],
            "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.put(url_for('categories.update_category', category_name="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_prov_map.query.filter.return_value.delete.assert_not_called()
        self.assertEqual(0, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_not_called()
        self.assertEqual(0, mock_instrument_map.query.filter.return_value.delete.call_count)

        mock_categories.query.filter.return_value.first.assert_not_called()
        self.assertEqual(0, mock_categories.query.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_category_404(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                 mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.put(url_for('categories.update_category', category_name="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_prov_map.query.filter.return_value.delete.assert_not_called()
        self.assertEqual(0, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_not_called()
        self.assertEqual(0, mock_instrument_map.query.filter.return_value.delete.call_count)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_404_instrument_not_found(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                             mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "Planning"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = None
        mock_category.provisions = []
        mock_category.instruments = []

        mock_stat_prov = MagicMock()
        mock_stat_prov.id = 1

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_instruments.query.filter.return_value.first.return_value = None
        mock_provisions.query.filter.return_value.first.return_value = mock_stat_prov

        response = self.client.put(url_for('categories.update_category', category_name="Planning"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_prov_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_instrument_map.query.filter.return_value.delete.call_count)
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_provisions.query.filter.return_value.first.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_404_stat_prov_not_found(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                            mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "Planning",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "Planning"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = None
        mock_category.provisions = []
        mock_category.instruments = []

        mock_instrument = MagicMock()
        mock_instrument.id = 1

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_instruments.query.filter.return_value.first.return_value = mock_instrument
        mock_provisions.query.filter.return_value.first.return_value = None

        response = self.client.put(url_for('categories.update_category', category_name="Planning"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_prov_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_instrument_map.query.filter.return_value.delete.call_count)
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_update_409(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                        mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "Planning"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = None
        mock_category.provisions = []
        mock_category.instruments = []

        mock_instrument = MagicMock()
        mock_instrument.id = 1

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        mock_instruments.query.filter.return_value.first.return_value = mock_instrument
        mock_provisions.query.filter.return_value.first.return_value = None

        response = self.client.put(url_for('categories.update_category', category_name="Planning"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_prov_map.query.filter.return_value.delete.assert_not_called()
        self.assertEqual(0, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_not_called()
        self.assertEqual(0, mock_instrument_map.query.filter.return_value.delete.call_count)
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)

        mock_validate.assert_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_sub_category_400(self, mock_categories, mock_db, mock_validate):

        data = {"namesssss": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.post(url_for('categories.create_sub_category', category="Planning"),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.filter.return_value.first.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_sub_category_parent_not_found(self, mock_categories, mock_db, mock_validate):

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.post(url_for('categories.create_sub_category', category="Planning"),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_sub_category_409(self, mock_categories, mock_db, mock_validate):

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = MagicMock()

        response = self.client.post(url_for('categories.create_sub_category', category="Planning"),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)

        mock_db.session.flush.assert_not_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_sub_category_provision_does_not_exist(self, mock_categories, mock_db, mock_provisions,
                                                       mock_validate):

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        mock_provisions.query.filter.return_value.first.return_value = None

        response = self.client.post(url_for('categories.create_sub_category', category="Planning"),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_sub_category_instrument_does_not_exist(self, mock_categories, mock_db, mock_provisions,
                                                        mock_instruments, mock_prov_map, mock_instrument_map,
                                                        mock_validate):

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        mock_instruments.query.filter.return_value.first.return_value = None
        mock_provisions.query.filter.return_value.first.return_value = MagicMock()

        response = self.client.post(url_for('categories.create_sub_category', category="Planning"),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_not_called()
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_db.session.add.assert_called()
        mock_validate.assert_called()
        mock_prov_map.assert_called()
        mock_instrument_map.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_add_sub_category_successful(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                         mock_prov_map, mock_instrument_map, mock_validate):

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        mock_provisions.query.filter.return_value.first.return_value = MagicMock()
        mock_instruments.query.filter.return_value.first.return_value = MagicMock()

        response = self.client.post(url_for('categories.create_sub_category', category="Planning"),
                                    data=json.dumps(data),
                                    headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 201)

        mock_db.session.flush.assert_called()
        mock_db.session.commit.assert_called()
        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_db.session.add.assert_called()
        mock_validate.assert_called()
        mock_prov_map.assert_called()
        mock_instrument_map.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_sub_category_parent_does_not_exist(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [None, None]

        response = self.client.get(url_for('categories.get_sub_category', category="Planning", sub_category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_sub_category_does_not_exist(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        response = self.client.get(url_for('categories.get_sub_category', category="Planning", sub_category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_get_sub_category_successful(self, mock_categories, mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_sub_category = MagicMock()
        mock_sub_category.name = "Child"
        mock_sub_category.display_name = "child display"
        mock_sub_category.permission = "child permission"

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [mock_parent, mock_category]

        mock_categories.query.filter.return_value.order_by.return_value.all.return_value = [mock_sub_category]

        response = self.client.get(url_for('categories.get_sub_category', category="Planning", sub_category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)

        self.assertEqual("abc", response.json["name"])
        self.assertEqual("display", response.json["display-name"])
        self.assertEqual("permission", response.json["permission"])
        self.assertEqual(['abc'], response.json["statutory-provisions"])
        self.assertEqual(['def'], response.json["instruments"])
        self.assertEqual("Child", response.json["sub-categories"][0]['name'])
        self.assertEqual("child display", response.json["sub-categories"][0]['display-name'])
        self.assertEqual("child permission", response.json["sub-categories"][0]['permission'])

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_categories.query.filter.return_value.order_by.return_value.all.assert_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_parent_not_found(self, mock_categories, mock_db, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [None, None]

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_not_found(self, mock_categories, mock_db, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_400(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        data = {"namesdfasdf": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 400)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_not_called()
        mock_validate.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_409(self, mock_categories, mock_db, mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [
            mock_parent, mock_category, MagicMock()]

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="def"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 409)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_provision_does_not_exist(self, mock_categories, mock_db, mock_provisions,
                                                       mock_instruments, mock_prov_map, mock_instrument_map,
                                                       mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [
            mock_parent, mock_category, MagicMock()]

        mock_provisions.query.filter.return_value.first.return_value = None
        mock_instruments.query.filter.return_value.first.return_value = None

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_instruments.query.filter.return_value.first.assert_not_called()
        mock_prov_map.assert_not_called()
        mock_instrument_map.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_instrument_does_not_exist(self, mock_categories, mock_db, mock_provisions,
                                                        mock_instruments, mock_prov_map, mock_instrument_map,
                                                        mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [
            mock_parent, mock_category, MagicMock()]

        mock_provisions.query.filter.return_value.first.return_value = MagicMock()
        mock_instruments.query.filter.return_value.first.return_value = None

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_prov_map.assert_called()
        mock_instrument_map.assert_not_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.Instruments')
    @patch('maintain_api.views.v1_0.categories.StatutoryProvision')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_put_sub_category_successful(self, mock_categories, mock_db, mock_provisions, mock_instruments,
                                         mock_prov_map, mock_instrument_map, mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [
            mock_parent, mock_category, MagicMock()]

        mock_provisions.query.filter.return_value.first.return_value = MagicMock()
        mock_instruments.query.filter.return_value.first.return_value = MagicMock()

        data = {"name": "New",
                "display-name": "Planning",
                "display-order": 11,
                "permission": None,
                "provisions": ["abc"],
                "instruments": ["def"]}

        response = self.client.put(url_for('categories.update_sub_category', category="Planning", sub_category="abc"),
                                   data=json.dumps(data),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        mock_validate.assert_called()
        mock_db.session.rollback.assert_not_called()
        mock_provisions.query.filter.return_value.first.assert_called()
        mock_instruments.query.filter.return_value.first.assert_called()
        mock_prov_map.assert_called()
        mock_instrument_map.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_sub_category_parent_not_found(self, mock_categories, mock_db, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [None, None]

        response = self.client.delete(url_for('categories.delete_sub_category',
                                              category="Planning", sub_category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_sub_category_not_found(self, mock_categories, mock_db, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        response = self.client.delete(url_for('categories.delete_sub_category',
                                              category="Planning", sub_category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
        mock_db.session.rollback.assert_called()

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_sub_category_no_children(self, mock_categories, mock_db, mock_prov_map,
                                             mock_instrument_map, mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [mock_parent, mock_category]
        mock_categories.query.filter.return_value.all.return_value = []

        response = self.client.delete(url_for('categories.delete_sub_category',
                                              category="Planning", sub_category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
        mock_db.session.rollback.assert_not_called()

        mock_prov_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(1, mock_instrument_map.query.filter.return_value.delete.call_count)

    @patch('maintain_api.app.validate')
    @patch('maintain_api.views.v1_0.categories.CategoryInstrumentsMapping')
    @patch('maintain_api.views.v1_0.categories.CategoryStatProvisionMapping')
    @patch('maintain_api.views.v1_0.categories.db')
    @patch('maintain_api.views.v1_0.categories.Categories')
    def test_delete_sub_category_with_children(self, mock_categories, mock_db, mock_prov_map,
                                               mock_instrument_map, mock_validate):

        mock_provision_mapping = MagicMock()
        mock_provision_mapping.provision.title = "abc"

        mock_instrument_mapping = MagicMock()
        mock_instrument_mapping.instrument.name = "def"

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.name = "parent"

        mock_category = MagicMock()
        mock_category.id = 1
        mock_category.name = "abc"
        mock_category.display_name = "display"
        mock_category.permission = "permission"
        mock_category.parent_id = 1
        mock_category.provisions = [mock_provision_mapping]
        mock_category.instruments = [mock_instrument_mapping]

        mock_child1 = MagicMock()
        mock_child1.id = 1

        mock_child2 = MagicMock()
        mock_child2.id = 2

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [mock_parent, mock_category]
        mock_categories.query.filter.return_value.all.return_value = [mock_child1, mock_child2]

        response = self.client.delete(url_for('categories.delete_sub_category',
                                              category="Planning", sub_category="abc"),
                                      headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 204)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
        mock_db.session.rollback.assert_not_called()

        mock_prov_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(3, mock_prov_map.query.filter.return_value.delete.call_count)
        mock_instrument_map.query.filter.return_value.delete.assert_called()
        self.assertEqual(3, mock_instrument_map.query.filter.return_value.delete.call_count)
