from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.ingredients.schemas import (
    IngredientCreateRequest,
    IngredientGroupCreateRequest,
    IngredientGroupUpdateRequest,
    IngredientUpdateRequest
)
from app.modules.ingredients.service import (
    create_ingredient,
    create_ingredient_group,
    delete_ingredient,
    delete_ingredient_group,
    update_ingredient,
    update_ingredient_group
)


router = APIRouter(
    tags=["Ingredients"]
)


def serialize_group(group):
    return {
        "id": group.id,
        "recipe_id": group.recipe_id,
        "group_name": group.group_name,
        "display_order": group.display_order
    }


def serialize_ingredient(ingredient):
    return {
        "id": ingredient.id,
        "ingredient_group_id": ingredient.ingredient_group_id,
        "ingredient_text": ingredient.ingredient_text,
        "display_order": ingredient.display_order
    }


@router.post("/api/v1/recipes/{recipe_id}/ingredient-groups")
def create_group_endpoint(
    recipe_id: int,
    payload: IngredientGroupCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    group = create_ingredient_group(
        db=db,
        recipe_id=recipe_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Ingredient group created successfully",
        data=serialize_group(group)
    )


@router.patch("/api/v1/ingredient-groups/{group_id}")
def update_group_endpoint(
    group_id: int,
    payload: IngredientGroupUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    group = update_ingredient_group(
        db=db,
        group_id=group_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Ingredient group updated successfully",
        data=serialize_group(group)
    )


@router.delete("/api/v1/ingredient-groups/{group_id}")
def delete_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    delete_ingredient_group(
        db=db,
        group_id=group_id,
        current_user=current_user
    )

    return success_response(
        message="Ingredient group deleted successfully"
    )


@router.post("/api/v1/ingredient-groups/{group_id}/ingredients")
def create_ingredient_endpoint(
    group_id: int,
    payload: IngredientCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ingredient = create_ingredient(
        db=db,
        group_id=group_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Ingredient created successfully",
        data=serialize_ingredient(ingredient)
    )


@router.patch("/api/v1/ingredients/{ingredient_id}")
def update_ingredient_endpoint(
    ingredient_id: int,
    payload: IngredientUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ingredient = update_ingredient(
        db=db,
        ingredient_id=ingredient_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Ingredient updated successfully",
        data=serialize_ingredient(ingredient)
    )


@router.delete("/api/v1/ingredients/{ingredient_id}")
def delete_ingredient_endpoint(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    delete_ingredient(
        db=db,
        ingredient_id=ingredient_id,
        current_user=current_user
    )

    return success_response(
        message="Ingredient deleted successfully"
    )