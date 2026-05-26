from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_optional_current_user
)
from app.modules.recipes.schemas import (
    RecipeCategoriesUpdateRequest,
    RecipeCreateRequest,
    RecipeUpdateRequest,
    RecipeVisibilityUpdateRequest
)
from app.modules.recipes.service import (
    assign_recipe_categories,
    create_recipe,
    delete_recipe,
    get_my_recipes,
    get_public_recipes,
    get_recipe_detail,
    update_recipe,
    update_recipe_visibility,
    upload_recipe_cover
)


router = APIRouter(
    prefix="/api/v1/recipes",
    tags=["Recipes"]
)


@router.post("")
def create_recipe_endpoint(
    payload: RecipeCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    recipe = create_recipe(
        db=db,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Recipe created successfully",
        data=recipe
    )


@router.patch("/{recipe_id}")
def update_recipe_endpoint(
    recipe_id: int,
    payload: RecipeUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    recipe = update_recipe(
        db=db,
        recipe_id=recipe_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Recipe updated successfully",
        data=recipe
    )


@router.delete("/{recipe_id}")
def delete_recipe_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    delete_recipe(
        db=db,
        recipe_id=recipe_id,
        current_user=current_user
    )

    return success_response(
        message="Recipe deleted successfully"
    )


@router.patch("/{recipe_id}/visibility")
def update_recipe_visibility_endpoint(
    recipe_id: int,
    payload: RecipeVisibilityUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    recipe = update_recipe_visibility(
        db=db,
        recipe_id=recipe_id,
        visibility=payload.visibility,
        current_user=current_user
    )

    return success_response(
        message="Recipe visibility updated successfully",
        data=recipe
    )


@router.put("/{recipe_id}/categories")
def update_recipe_categories_endpoint(
    recipe_id: int,
    payload: RecipeCategoriesUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    recipe = assign_recipe_categories(
        db=db,
        recipe_id=recipe_id,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Recipe categories updated successfully",
        data=recipe
    )


@router.post("/{recipe_id}/cover-image")
def upload_recipe_cover_endpoint(
    recipe_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    recipe = upload_recipe_cover(
        db=db,
        recipe_id=recipe_id,
        file=file,
        current_user=current_user
    )

    return success_response(
        message="Recipe cover uploaded successfully",
        data=recipe
    )


@router.get("")
def list_public_recipes(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    category_ids: list[int] | None = Query(default=None),
    contains_pork: bool | None = None,
    contains_alcohol: bool | None = None,
    max_cooking_time: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    result = get_public_recipes(
        db=db,
        page=page,
        limit=limit,
        search=search,
        category_ids=category_ids,
        contains_pork=contains_pork,
        contains_alcohol=contains_alcohol,
        max_cooking_time=max_cooking_time,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user
    )

    return success_response(
        message="Recipes fetched successfully",
        data=result
    )


@router.get("/me")
def list_my_recipes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    recipes = get_my_recipes(
        db=db,
        current_user=current_user
    )

    return success_response(
        message="My recipes fetched successfully",
        data=recipes
    )


@router.get("/{recipe_id}")
def recipe_detail(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    recipe = get_recipe_detail(
        db=db,
        recipe_id=recipe_id,
        current_user=current_user
    )

    return success_response(
        message="Recipe detail fetched successfully",
        data=recipe
    )