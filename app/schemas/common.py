"""Skema umum: pagination dan format error."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]


class ErrorResponse(BaseModel):
    status: str = "error"
    code: str
    path: str
    details: str | list[dict]
