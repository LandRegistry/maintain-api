from flask import Blueprint, Response, current_app, request
from maintain_api.models import Categories, StatutoryProvision, Instruments, \
    CategoryStatProvisionMapping, CategoryInstrumentsMapping
from maintain_api.exceptions import ApplicationError
from sqlalchemy import func
import json
from maintain_api.extensions import db
from jsonschema import validate, ValidationError

categories = Blueprint('categories', __name__, url_prefix='/v1.0/maintain/categories')

CATEGORY_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "display-name": {"type": "string"},
        "display-order": {"type": "integer"},
        "permission": {"type": ["string", "null"]},
        "provisions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "instruments": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "additionalProperties": False,
    "required": ["name", "display-name", "display-order", "permission", "provisions", "instruments"]
}


@categories.route('', methods=['GET'])
def get_all_categories():
    current_app.logger.info("Get all categories")

    all_categories = Categories.query\
        .filter(Categories.parent_id == None) \
        .order_by(Categories.display_order) \
        .all()  # noqa: E711 - Ignore "is None vs ==" linting error, is None does not produce valid sql in sqlAlchmey

    results = []
    for category in all_categories:
        result_json = {
            "permission": category.permission,
            "display-name": category.display_name,
            "name": category.name
        }
        results.append(result_json)

    return Response(response=json.dumps(results), mimetype="application/json")


@categories.route('', methods=['POST'])
def add_categories():
    current_app.logger.info("Add category")

    request_body = request.get_json()

    try:
        validate(request_body, CATEGORY_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Create category - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    name = request_body["name"]
    display_name = request_body["display-name"]
    display_order = request_body["display-order"]
    permission = request_body["permission"]
    provisions = request_body["provisions"]
    instruments = request_body["instruments"]

    try:
        exists = Categories.query\
            .filter(func.lower(Categories.name) == func.lower(name)) \
            .filter(Categories.parent_id == None) \
            .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey

        if exists is not None:
            message = "Category '{0}' already exists.".format(name)
            current_app.logger.info(message)
            raise ApplicationError(message, 409, 409)

        category = Categories(name, None, display_order, permission, display_name)
        db.session.add(category)
        db.session.flush()

        for prov in provisions:
            provision = StatutoryProvision.query\
                .filter(func.lower(StatutoryProvision.title) == func.lower(prov)).first()
            if provision is None:
                message = "Statutory provision '{0}' does not exist.".format(prov)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryStatProvisionMapping(category.id, provision.id)
            db.session.add(mapping)

        for instrument in instruments:
            exists = Instruments.query.filter(func.lower(Instruments.name) == func.lower(instrument)).first()
            if exists is None:
                message = "Instrument '{0}' does not exist.".format(instrument)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryInstrumentsMapping(category.id, exists.id)
            db.session.add(mapping)

        db.session.commit()

        return "", 201

    except Exception:
        current_app.logger.info("Rolling back transaction")
        db.session.rollback()
        raise


@categories.route('/<category>', methods=['GET'])
def get_category(category):
    current_app.logger.info("Get category for {0}.".format(category))

    category_obj = Categories.query \
        .filter(func.lower(Categories.name) == func.lower(category)) \
        .filter(Categories.parent_id == None) \
        .first()  # noqa: E711 - Ignore "is None vs ==" linting error, is None does not produce valid sql in sqlAlchmey

    if category_obj is None:
        raise ApplicationError("Category '{0}' not found.".format(category), 404, 404)

    provisions = []
    for provision_mapping in category_obj.provisions:
        provisions.append(provision_mapping.provision.title)

    instruments = []
    for instruments_mapping in category_obj.instruments:
        instruments.append(instruments_mapping.instrument.name)

    children = []
    for children_mapping in Categories.query\
            .filter(Categories.parent_id == category_obj.id)\
            .order_by(Categories.display_order).all():
        children.append(
            {
                "name": children_mapping.name,
                "display-name": children_mapping.display_name,
                "permission": children_mapping.permission,

            })

    result = {
        "name": category_obj.name,
        "display-name": category_obj.display_name,
        "permission": category_obj.permission,
        "statutory-provisions": provisions,
        "instruments": instruments,
        "sub-categories": children}

    return Response(response=json.dumps(result), mimetype="application/json")


@categories.route('/<category>', methods=['DELETE'])
def delete_category(category):
    current_app.logger.info("Delete category for {0}.".format(category))

    try:
        category = Categories.query \
            .filter(func.lower(Categories.name) == func.lower(category)) \
            .filter(Categories.parent_id == None) \
            .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey

        if category is None:
            raise ApplicationError("Category '{0}' not found.".format(category), 404, 404)

        sub_categories = Categories.query \
            .filter(Categories.parent_id == category.id) \
            .all()

        for sub_category in sub_categories:
            CategoryInstrumentsMapping.query\
                .filter(CategoryInstrumentsMapping.category_id == sub_category.id).delete()
            CategoryStatProvisionMapping.query\
                .filter(CategoryStatProvisionMapping.category_id == sub_category.id).delete()
            Categories.query\
                .filter(Categories.id == sub_category.id).delete()

        CategoryInstrumentsMapping.query.filter(CategoryInstrumentsMapping.category_id == category.id).delete()
        CategoryStatProvisionMapping.query.filter(CategoryStatProvisionMapping.category_id == category.id).delete()
        Categories.query.filter(Categories.id == category.id).delete()

        db.session.commit()

        return "", 204

    except Exception:
        current_app.logger.info("Rolling back transaction")
        db.session.rollback()
        raise


@categories.route('/<category_name>', methods=['PUT'])
def update_category(category_name):
    current_app.logger.info("Update category")

    request_body = request.get_json()

    try:
        validate(request_body, CATEGORY_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Update category - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    name = request_body["name"]
    display_name = request_body["display-name"]
    display_order = request_body["display-order"]
    permission = request_body["permission"]
    provisions = request_body["provisions"]
    instruments = request_body["instruments"]

    try:
        category = Categories.query\
            .filter(func.lower(Categories.name) == func.lower(category_name)) \
            .filter(Categories.parent_id == None) \
            .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey

        if category is None:
            message = "Category '{0}' does not exist.".format(category_name)
            current_app.logger.info(message)
            raise ApplicationError(message, 404, 404)

        if category.name.lower() != name.lower():
            inuse = Categories.query\
                .filter(func.lower(Categories.name) == func.lower(name)) \
                .filter(Categories.parent_id == None) \
                .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey
            if inuse is not None:
                message = "Category with the name '{0}' already exists.".format(name)
                current_app.logger.info(message)
                raise ApplicationError(message, 409, 409)

        category.name = name
        category.display_name = display_name
        category.permission = permission
        category.display_order = display_order

        CategoryInstrumentsMapping.query.filter(CategoryInstrumentsMapping.category_id == category.id).delete()
        CategoryStatProvisionMapping.query.filter(CategoryStatProvisionMapping.category_id == category.id).delete()

        for prov in provisions:
            provision = StatutoryProvision.query\
                .filter(func.lower(StatutoryProvision.title) == func.lower(prov)).first()
            if provision is None:
                message = "Statutory provision '{0}' does not exist.".format(prov)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryStatProvisionMapping(category.id, provision.id)
            db.session.add(mapping)

        for instrument in instruments:
            exists = Instruments.query.filter(func.lower(Instruments.name) == func.lower(instrument)).first()
            if exists is None:
                message = "Instrument '{0}' does not exist.".format(instrument)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryInstrumentsMapping(category.id, exists.id)
            db.session.add(mapping)

        db.session.commit()

        return "", 204

    except Exception:
        current_app.logger.info("Rolling back transaction")
        db.session.rollback()
        raise


@categories.route('/<category>/sub-categories', methods=['POST'])
def create_sub_category(category):
    current_app.logger.info("Add sub category")
    request_body = request.get_json()

    try:
        validate(request_body, CATEGORY_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Create category - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    name = request_body["name"]
    display_name = request_body["display-name"]
    display_order = request_body["display-order"]
    permission = request_body["permission"]
    provisions = request_body["provisions"]
    instruments = request_body["instruments"]

    try:

        parent_obj = Categories.query\
            .filter(func.lower(Categories.name) == func.lower(category)) \
            .filter(Categories.parent_id == None) \
            .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey
        if parent_obj is None:
            message = "Parent '{0}' does not exist.".format(category)
            current_app.logger.info(message)
            raise ApplicationError(message, 404, 404)

        exists = Categories.query\
            .filter(func.lower(Categories.name) == func.lower(name))\
            .filter(Categories.parent_id == parent_obj.id)\
            .first()

        if exists is not None:
            message = "Sub-category '{0}' already exists under {1}".format(name, category)
            current_app.logger.info(message)
            raise ApplicationError(message, 409, 409)

        category = Categories(name, parent_obj.id, display_order, permission, display_name)
        db.session.add(category)
        db.session.flush()

        for prov in provisions:
            provision = StatutoryProvision.query \
                .filter(func.lower(StatutoryProvision.title) == func.lower(prov)).first()
            if provision is None:
                message = "Statutory provision '{0}' does not exist.".format(prov)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryStatProvisionMapping(category.id, provision.id)
            db.session.add(mapping)

        for instrument in instruments:
            exists = Instruments.query\
                .filter(func.lower(Instruments.name) == func.lower(instrument)).first()
            if exists is None:
                message = "Instrument '{0}' does not exist.".format(instrument)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryInstrumentsMapping(category.id, exists.id)
            db.session.add(mapping)

        db.session.commit()

        return "", 201

    except Exception:
        current_app.logger.info("Rolling back transaction")
        db.session.rollback()
        raise


@categories.route('/<category>/sub-categories/<path:sub_category>', methods=['GET'])
def get_sub_category(category, sub_category):
    current_app.logger.info("Get category for {0}.".format(category))

    category_obj = Categories.query \
        .filter(func.lower(Categories.name) == func.lower(category)) \
        .filter(Categories.parent_id == None) \
        .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey

    if category_obj is None:
        raise ApplicationError("Category '{0}' not found.".format(category), 404, 404)

    sub_category_obj = Categories.query \
        .filter(func.lower(Categories.name) == func.lower(sub_category)) \
        .filter(Categories.parent_id == category_obj.id) \
        .first()

    if sub_category_obj is None:
        raise ApplicationError("Sub-category '{0}' not found for parent '{1}'".format(sub_category, category),
                               404, 404)

    provisions = []
    for provision_mapping in sub_category_obj.provisions:
        provisions.append(provision_mapping.provision.title)

    instruments = []
    for instruments_mapping in sub_category_obj.instruments:
        instruments.append(instruments_mapping.instrument.name)

    children = []
    for children_mapping in Categories.query \
            .filter(Categories.parent_id == sub_category_obj.id) \
            .order_by(Categories.display_order).all():
        children.append(
            {
                "name": children_mapping.name,
                "display-name": children_mapping.display_name,
                "permission": children_mapping.permission,

            })

    result = {
        "name": sub_category_obj.name,
        "display-name": sub_category_obj.display_name,
        "permission": sub_category_obj.permission,
        "statutory-provisions": provisions,
        "instruments": instruments,
        "sub-categories": children,
        "parent": category_obj.name}

    return Response(response=json.dumps(result), mimetype="application/json")


@categories.route('/<category>/sub-categories/<path:sub_category>', methods=['PUT'])
def update_sub_category(category, sub_category):
    current_app.logger.info("Update category")

    request_body = request.get_json()

    try:
        validate(request_body, CATEGORY_SCHEMA)
    except ValidationError as e:
        current_app.logger.info("Update category - payload failed validation")
        raise ApplicationError(e.message, 400, 400)

    name = request_body["name"]
    display_name = request_body["display-name"]
    display_order = request_body["display-order"]
    permission = request_body["permission"]
    provisions = request_body["provisions"]
    instruments = request_body["instruments"]

    try:
        parent = Categories.query \
            .filter(func.lower(Categories.name) == func.lower(category)) \
            .filter(Categories.parent_id == None) \
            .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey

        if parent is None:
            message = "Category '{0}' does not exist.".format(category)
            current_app.logger.info(message)
            raise ApplicationError(message, 404, 404)

        sub_category_obj = Categories.query \
            .filter(func.lower(Categories.name) == func.lower(sub_category)) \
            .filter(Categories.parent_id == parent.id) \
            .first()

        if sub_category_obj is None:
            raise ApplicationError("Sub-category '{0}' not found for parent '{1}'"
                                   .format(sub_category, category), 404, 404)

        if sub_category_obj.name.lower() != sub_category.lower():
            inuse = Categories.query \
                .filter(func.lower(Categories.name) == func.lower(sub_category)) \
                .filter(Categories.parent_id == parent.id) \
                .first()
            if inuse is not None:
                message = "sub-category with the name '{0}' already exists under {1}.".format(name, category)
                current_app.logger.info(message)
                raise ApplicationError(message, 409, 409)

        sub_category_obj.name = name
        sub_category_obj.display_name = display_name
        sub_category_obj.permission = permission
        sub_category_obj.display_order = display_order

        CategoryInstrumentsMapping.query.filter(CategoryInstrumentsMapping.category_id == sub_category_obj.id).delete()
        CategoryStatProvisionMapping.query.filter(
            CategoryStatProvisionMapping.category_id == sub_category_obj.id).delete()

        for prov in provisions:
            provision = StatutoryProvision.query \
                .filter(func.lower(StatutoryProvision.title) == func.lower(prov)).first()
            if provision is None:
                message = "Statutory provision '{0}' does not exist.".format(prov)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryStatProvisionMapping(sub_category_obj.id, provision.id)
            db.session.add(mapping)

        for instrument in instruments:
            exists = Instruments.query.filter(func.lower(Instruments.name) == func.lower(instrument)).first()
            if exists is None:
                message = "Instrument '{0}' does not exist.".format(instrument)
                current_app.logger.info(message)
                raise ApplicationError(message, 404, 404)
            mapping = CategoryInstrumentsMapping(sub_category_obj.id, exists.id)
            db.session.add(mapping)

        db.session.commit()

        return "", 204

    except Exception:
        current_app.logger.info("Rolling back transaction")
        db.session.rollback()
        raise


@categories.route('/<category>/sub-categories/<path:sub_category>', methods=['DELETE'])
def delete_sub_category(category, sub_category):
    current_app.logger.info("Delete category for {0}.".format(category))

    try:
        category = Categories.query \
            .filter(func.lower(Categories.name) == func.lower(category)) \
            .filter(Categories.parent_id == None) \
            .first()  # noqa: E711 - Ignore "is None vs ==", is None does not produce valid sql in sqlAlchmey

        if category is None:
            raise ApplicationError("Category '{0}' not found.".format(category), 404, 404)

        sub_category_obj = Categories.query \
            .filter(func.lower(Categories.name) == func.lower(sub_category)) \
            .filter(Categories.parent_id == category.id) \
            .first()

        if sub_category_obj is None:
            raise ApplicationError("Sub-category '{0}' not found for parent '{1}'"
                                   .format(sub_category, category), 404, 404)

        sub_categories = Categories.query \
            .filter(Categories.parent_id == sub_category_obj.id) \
            .all()

        for sub_category in sub_categories:
            CategoryInstrumentsMapping.query \
                .filter(CategoryInstrumentsMapping.category_id == sub_category.id).delete()
            CategoryStatProvisionMapping.query \
                .filter(CategoryStatProvisionMapping.category_id == sub_category.id).delete()
            Categories.query \
                .filter(Categories.id == sub_category.id).delete()

        CategoryInstrumentsMapping.query\
            .filter(CategoryInstrumentsMapping.category_id == sub_category_obj.id).delete()
        CategoryStatProvisionMapping.query\
            .filter(CategoryStatProvisionMapping.category_id == sub_category_obj.id).delete()
        Categories.query\
            .filter(Categories.id == sub_category_obj.id).delete()

        db.session.commit()

        return "", 204

    except Exception:
        current_app.logger.info("Rolling back transaction")
        db.session.rollback()
        raise
