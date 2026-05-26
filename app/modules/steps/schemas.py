from pydantic import BaseModel, Field


class RecipeStepCreateRequest(BaseModel):
    step_number: int = Field(..., ge=1)
    instruction_text: str = Field(..., min_length=1)


class RecipeStepUpdateRequest(BaseModel):
    step_number: int | None = Field(default=None, ge=1)
    instruction_text: str | None = Field(default=None, min_length=1)


class StepImageCreateRequest(BaseModel):
    display_order: int = Field(..., ge=1)