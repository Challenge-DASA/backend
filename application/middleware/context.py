import uuid
import datetime
from quart import g, request

from domain.context import Context, UserId
from application.config import get_config

config = get_config()


class ContextMiddleware:

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    async def before_request(self):
        user_id = await self._extract_user_id()

        context = Context(
            request_id=uuid.uuid4(),
            request_datetime=datetime.datetime.now(datetime.timezone.utc),
            user_id=user_id
        )

        g.context = context

    @staticmethod
    async def after_request(response):
        if hasattr(g, 'context') and config.ENABLE_REQUEST_LOGGING:
            context = g.context
            print(f"Request {context.request_id} completed at {context.request_datetime}")

        return response

    @staticmethod
    async def _extract_user_id() -> UserId:
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            return config.TEMP_USER_ID

        return config.TEMP_USER_ID


def get_context() -> Context:
    if not hasattr(g, 'context'):
        raise RuntimeError("Context not available. Make sure ContextMiddleware is registered.")

    return g.context