from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(AppSchema):
    id: int
    created_at: datetime
    updated_at: datetime
