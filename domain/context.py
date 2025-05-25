import datetime
import uuid

from pydantic import BaseModel

from domain.value_objects.ids import UserId


class Context(BaseModel):
    request_id: uuid.UUID
    request_datetime: datetime.datetime
    user_id: UserId
