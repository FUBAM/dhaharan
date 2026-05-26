from pydantic import BaseModel, Field


class IngredientGroupCreateRequest(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=100)
    display_order: int = Field(..., ge=1)


class IngredientGroupUpdateRequest(BaseModel):
    group_name: str | None = Field(default=None, min_length=1, max_length=100)
    display_order: int | None = Field(default=None, ge=1)


class IngredientCreateRequest(BaseModel):
    ingredient_text: str = Field(..., min_length=1, max_length=500)
    display_order: int = Field(..., ge=1)


class IngredientUpdateRequest(BaseModel):
    ingredient_text: str | None = Field(default=None, min_length=1, max_length=500)
    display_order: int | None = Field(default=None, ge=1)