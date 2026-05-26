from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.steps.schemas import (
    RecipeStepCreateRequest,
    RecipeStepUpdateRequest
)
from app.modules.steps.service import (
    create_step,
    delete_step,
    delete_step_image,
    update_step,
    upload_step_image
)


router = APIRouter(
    tags=["Recipe Steps"]
)


def serialize_step(step):
    return {
        "id": step.id,
        "recipe_id": step.recipe_id,
        "step_number": step.step_number,
        "instruction_text": step.instruction_text
    }


def serialize_step_image(image):
    return {
        "id": image.id,
        "recipe_step_id": image.recipe_step_id,
        "image_url": image.image_url,
        "display_order": image.display_order
    }


@router.post("/api/v1/recipes/{recipe_id}/steps")
def create_step_endpoint(
    recipe_id: int,
    payload: RecipeStepCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    step = create_step(
        db=db,
        recipe_id=recipe_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Recipe step created successfully",
        data=serialize_step(step)
    )


@router.patch("/api/v1/steps/{step_id}")
def update_step_endpoint(
    step_id: int,
    payload: RecipeStepUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    step = update_step(
        db=db,
        step_id=step_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Recipe step updated successfully",
        data=serialize_step(step)
    )


@router.delete("/api/v1/steps/{step_id}")
def delete_step_endpoint(
    step_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    delete_step(
        db=db,
        step_id=step_id,
        current_user=current_user
    )

    return success_response(
        message="Recipe step deleted successfully"
    )


@router.post("/api/v1/steps/{step_id}/images")
def upload_step_image_endpoint(
    step_id: int,
    display_order: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    image = upload_step_image(
        db=db,
        step_id=step_id,
        display_order=display_order,
        file=file,
        current_user=current_user
    )

    return success_response(
        message="Step image uploaded successfully",
        data=serialize_step_image(image)
    )


@router.delete("/api/v1/step-images/{image_id}")
def delete_step_image_endpoint(
    image_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    delete_step_image(
        db=db,
        image_id=image_id,
        current_user=current_user
    )

    return success_response(
        message="Step image deleted successfully"
    )