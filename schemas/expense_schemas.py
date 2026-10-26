from datetime import date
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    date: date
    category_id: int = Field(gt=0)
    transaction_type: Literal["income", "expense"] = "expense"

    @field_validator("title", mode="before")
    @classmethod
    def clear_title(cls, v: Any) -> Any: 
        if isinstance(v, str):
            return v.strip()
        return v

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: Decimal
    date: date
    category_id: int
    transaction_type: Literal["income", "expense"]

class StatisticsResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal