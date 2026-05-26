from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.common.enums import VisibilityEnum
from app.common.schemas import (
    CategoryResponse,
    CounterResponse,
    InteractionStateResponse,
    UserSummary
)


class RecipeCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    cooking_time_minutes: int = Field(..., gt=0)
    servings: int = Field(..., gt=0)
    cooking_cost: Decimal = Field(..., ge=0)
    contains_pork: bool = False
    contains_alcohol: bool = False
    visibility: VisibilityEnum = VisibilityEnum.private


class RecipeUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    cooking_time_minutes: int | None = Field(default=None, gt=0)
    servings: int | None = Field(default=None, gt=0)
    cooking_cost: Decimal | None = Field(default=None, ge=0)
    contains_pork: bool | None = None
    contains_alcohol: bool | None = None


class RecipeVisibilityUpdateRequest(BaseModel):
    visibility: VisibilityEnum


class RecipeCategoriesUpdateRequest(BaseModel):
    category_ids: list[int]


class RecipeSummaryResponse(BaseModel):
    id: int
    title: str
    description: str | None
    cover_image_url: str | None

    cooking_time_minutes: int
    servings: int
    cooking_cost: Decimal

    contains_pork: bool
    contains_alcohol: bool
    visibility: VisibilityEnum

    author: UserSummary
    categories: list[CategoryResponse]

    counters: CounterResponse
    interaction_state: InteractionStateResponse

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class IngredientResponse(BaseModel):
    id: int
    ingredient_text: str
    display_order: int


class IngredientGroupResponse(BaseModel):
    id: int
    group_name: str
    display_order: int
    ingredients: list[IngredientResponse]


class StepImageResponse(BaseModel):
    id: int
    image_url: str
    display_order: int


class RecipeStepResponse(BaseModel):
    id: int
    step_number: int
    instruction_text: str
    images: list[StepImageResponse]


class RecipeDetailResponse(BaseModel):
    id: int
    title: str
    description: str | None
    cover_image_url: str | None

    cooking_time_minutes: int
    servings: int
    cooking_cost: Decimal

    contains_pork: bool
    contains_alcohol: bool
    visibility: VisibilityEnum

    author: UserSummary
    categories: list[CategoryResponse]

    ingredient_groups: list[IngredientGroupResponse]
    steps: list[RecipeStepResponse]

    counters: CounterResponse
    interaction_state: InteractionStateResponse

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }