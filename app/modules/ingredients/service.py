from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.ingredients.models import Ingredient, IngredientGroup
from app.modules.ingredients.schemas import (
    IngredientCreateRequest,
    IngredientGroupCreateRequest,
    IngredientGroupUpdateRequest,
    IngredientUpdateRequest
)
from app.modules.recipes.service import get_recipe_by_id
from app.modules.users.models import User


def validate_recipe_owner(recipe, current_user: User):
    if recipe.user_id != current_user.id:
        raise ForbiddenException("You do not own this recipe")


def get_group_by_id(
    db: Session,
    group_id: int
) -> IngredientGroup | None:
    return (
        db.query(IngredientGroup)
        .options(
            joinedload(IngredientGroup.recipe),
            joinedload(IngredientGroup.ingredients)
        )
        .filter(IngredientGroup.id == group_id)
        .first()
    )


def get_ingredient_by_id(
    db: Session,
    ingredient_id: int
) -> Ingredient | None:
    return (
        db.query(Ingredient)
        .options(
            joinedload(Ingredient.group).joinedload(IngredientGroup.recipe)
        )
        .filter(Ingredient.id == ingredient_id)
        .first()
    )


def create_ingredient_group(
    db: Session,
    recipe_id: int,
    payload: IngredientGroupCreateRequest,
    current_user: User
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    group = IngredientGroup(
        recipe_id=recipe.id,
        group_name=payload.group_name,
        display_order=payload.display_order
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return group


def update_ingredient_group(
    db: Session,
    group_id: int,
    payload: IngredientGroupUpdateRequest,
    current_user: User
):
    group = get_group_by_id(db, group_id)

    if not group:
        raise NotFoundException("Ingredient group not found")

    validate_recipe_owner(group.recipe, current_user)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    return group


def delete_ingredient_group(
    db: Session,
    group_id: int,
    current_user: User
):
    group = get_group_by_id(db, group_id)

    if not group:
        raise NotFoundException("Ingredient group not found")

    validate_recipe_owner(group.recipe, current_user)

    db.delete(group)
    db.commit()


def create_ingredient(
    db: Session,
    group_id: int,
    payload: IngredientCreateRequest,
    current_user: User
):
    group = get_group_by_id(db, group_id)

    if not group:
        raise NotFoundException("Ingredient group not found")

    validate_recipe_owner(group.recipe, current_user)

    ingredient = Ingredient(
        ingredient_group_id=group.id,
        ingredient_text=payload.ingredient_text,
        display_order=payload.display_order
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return ingredient


def update_ingredient(
    db: Session,
    ingredient_id: int,
    payload: IngredientUpdateRequest,
    current_user: User
):
    ingredient = get_ingredient_by_id(db, ingredient_id)

    if not ingredient:
        raise NotFoundException("Ingredient not found")

    validate_recipe_owner(
        ingredient.group.recipe,
        current_user
    )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)

    return ingredient


def delete_ingredient(
    db: Session,
    ingredient_id: int,
    current_user: User
):
    ingredient = get_ingredient_by_id(db, ingredient_id)

    if not ingredient:
        raise NotFoundException("Ingredient not found")

    validate_recipe_owner(
        ingredient.group.recipe,
        current_user
    )

    db.delete(ingredient)
    db.commit()