from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
