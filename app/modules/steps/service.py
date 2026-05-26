from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload

from app.common.upload import validate_image_upload
from app.core.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.recipes.service import get_recipe_by_id
from app.modules.steps.models import RecipeStep, RecipeStepImage
from app.modules.steps.schemas import (
    RecipeStepCreateRequest,
    RecipeStepUpdateRequest
)
from app.modules.users.models import User


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


def validate_recipe_owner(recipe, current_user: User):
    if recipe.user_id != current_user.id:
        raise ForbiddenException("You do not own this recipe")


def get_step_by_id(
    db: Session,
    step_id: int
) -> RecipeStep | None:
    return (
        db.query(RecipeStep)
        .options(
            joinedload(RecipeStep.recipe),
            joinedload(RecipeStep.images)
        )
        .filter(RecipeStep.id == step_id)
        .first()
    )


def get_step_image_by_id(
    db: Session,
    image_id: int
) -> RecipeStepImage | None:
    return (
        db.query(RecipeStepImage)
        .options(
            joinedload(RecipeStepImage.step).joinedload(RecipeStep.recipe)
        )
        .filter(RecipeStepImage.id == image_id)
        .first()
    )


def create_step(
    db: Session,
    recipe_id: int,
    payload: RecipeStepCreateRequest,
    current_user: User
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    step = RecipeStep(
        recipe_id=recipe.id,
        step_number=payload.step_number,
        instruction_text=payload.instruction_text
    )

    db.add(step)
    db.commit()
    db.refresh(step)

    return step


def update_step(
    db: Session,
    step_id: int,
    payload: RecipeStepUpdateRequest,
    current_user: User
):
    step = get_step_by_id(db, step_id)

    if not step:
        raise NotFoundException("Recipe step not found")

    validate_recipe_owner(step.recipe, current_user)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(step, field, value)

    db.commit()
    db.refresh(step)

    return step


def delete_step(
    db: Session,
    step_id: int,
    current_user: User
):
    step = get_step_by_id(db, step_id)

    if not step:
        raise NotFoundException("Recipe step not found")

    validate_recipe_owner(step.recipe, current_user)

    db.delete(step)
    db.commit()


def upload_step_image(
    db: Session,
    step_id: int,
    display_order: int,
    file: UploadFile,
    current_user: User
):
    step = get_step_by_id(db, step_id)

    if not step:
        raise NotFoundException("Recipe step not found")

    validate_recipe_owner(step.recipe, current_user)

    validate_image_upload(file)

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ForbiddenException("Unsupported file type")

    filename = f"{uuid4()}{extension}"
    save_path = Path("app/uploads/recipe_steps") / filename

    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    image = RecipeStepImage(
        recipe_step_id=step.id,
        image_url=f"{settings.BASE_URL}/uploads/recipe_steps/{filename}",
        display_order=display_order
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image


def delete_step_image(
    db: Session,
    image_id: int,
    current_user: User
):
    image = get_step_image_by_id(db, image_id)

    if not image:
        raise NotFoundException("Step image not found")

    validate_recipe_owner(
        image.step.recipe,
        current_user
    )

    db.delete(image)
    db.commit()