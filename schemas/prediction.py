"""Strict input validation for advertisement moderation."""

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    seller_id: int = Field(gt=0)
    is_verified_seller: bool
    item_id: int = Field(gt=0)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: int = Field(gt=0)
    images_qty: int = Field(ge=0)


class ValidationErrorDetail(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorDetail]


class ErrorResponse(BaseModel):
    detail: str
