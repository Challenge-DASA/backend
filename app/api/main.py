from quart import Quart
from quart_schema import QuartSchema, Info, Tag

from app.api.error_handlers import register_error_handlers
from app.api.routes import register_blueprints
from application.config import get_config
from application.middleware.context import ContextMiddleware

config = get_config()
app = Quart(__name__)
app.config.from_object(config)

QuartSchema(
    app,
    info=Info(
        title="SmartLab API",
        version="1.0.0",
        description="API for managing SmartLab",
    ),
)

context_middleware = ContextMiddleware(app)

register_error_handlers(app)
register_blueprints(app)

if __name__ == "__main__":
    app.run(debug=config.DEBUG)