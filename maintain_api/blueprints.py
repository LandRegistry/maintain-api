# Import every blueprint file
from maintain_api.views import general
from maintain_api.views.v1_0 import statutory_provisions as statutory_provision_v1_0
from maintain_api.views.v1_0 import add_land_charge as add_land_charge_v1_0
from maintain_api.views.v1_0 import update_land_charge as update_land_charge_v1_0
from maintain_api.views.v1_0 import categories as categories_v1_0
from maintain_api.views.v1_0 import instruments as instruments_v1_0


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(add_land_charge_v1_0.add_land_charge_bp, url_prefix='/v1.0/maintain')
    app.register_blueprint(update_land_charge_v1_0.update_land_charge_bp, url_prefix='/v1.0/maintain')
    app.register_blueprint(statutory_provision_v1_0.statutory_provision_bp, url_prefix='/v1.0/maintain')
    app.register_blueprint(categories_v1_0.categories)
    app.register_blueprint(instruments_v1_0.instruments_bp)

    # All done!
    app.logger.info("Blueprints registered")
