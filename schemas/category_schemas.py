from typing import Any

from pydantic import BaseModel, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

    @field_validator("name", mode="before")
    @classmethod
    def clear_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v


class CategoryResponse(BaseModel):
    id: int
    name: str
