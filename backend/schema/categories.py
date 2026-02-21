from datetime import datetime

from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
