from quart import Quart
from app.api.blueprints.laboratory import laboratory_bp
from app.api.blueprints.procedure import procedures_bp, transactions_bp
from app.api.blueprints.system import system_bp


def register_blueprints(app: Quart) -> None:
    app.register_blueprint(laboratory_bp)
    app.register_blueprint(procedures_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(system_bp)