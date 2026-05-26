from math import ceil
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.common.upload import validate_image_upload
from app.common.schemas import (
    CategoryResponse,
    PaginationMeta,
    PaginatedData,
    UserSummary
)
from app.core.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.categories.models import Category
from app.modules.ingredients.models import IngredientGroup
from app.modules.recipes.models import Recipe, RecipeCategory
from app.modules.recipes.schemas import (
    IngredientGroupResponse,
    IngredientResponse,
    RecipeCategoriesUpdateRequest,
    RecipeCreateRequest,
    RecipeDetailResponse,
    RecipeStepResponse,
    RecipeSummaryResponse,
    RecipeUpdateRequest,
    StepImageResponse
)
from app.modules.social.service import (
    get_interaction_state,
    get_recipe_counters
)
from app.modules.steps.models import RecipeStep
from app.modules.users.models import User
from app.modules.social.models import (
    Bookmark,
    Comment,
    Follow,
    RecipeLike
)


def get_recipe_by_id(
    db: Session,
    recipe_id: int
) -> Recipe | None:
    return (
        db.query(Recipe)
        .options(
            joinedload(Recipe.author),
            joinedload(Recipe.categories).joinedload(RecipeCategory.category),
            joinedload(Recipe.ingredient_groups).joinedload(
                IngredientGroup.ingredients
            ),
            joinedload(Recipe.steps).joinedload(
                RecipeStep.images
            )
        )
        .filter(
            Recipe.id == recipe_id,
            Recipe.deleted_at.is_(None)
        )
        .first()
    )


def validate_recipe_owner(
    recipe: Recipe,
    user: User
):
    if recipe.user_id != user.id:
        raise ForbiddenException("You do not own this recipe")


def get_recipe_counters_batch(
    db: Session,
    recipe_ids: list[int]
):
    if not recipe_ids:
        return {}

    likes = dict(
        db.query(
            RecipeLike.recipe_id,
            func.count(RecipeLike.id)
        )
        .filter(
            RecipeLike.recipe_id.in_(recipe_ids)
        )
        .group_by(RecipeLike.recipe_id)
        .all()
    )

    comments = dict(
        db.query(
            Comment.recipe_id,
            func.count(Comment.id)
        )
        .filter(
            Comment.recipe_id.in_(recipe_ids)
        )
        .group_by(Comment.recipe_id)
        .all()
    )

    bookmarks = dict(
        db.query(
            Bookmark.recipe_id,
            func.count(Bookmark.id)
        )
        .filter(
            Bookmark.recipe_id.in_(recipe_ids)
        )
        .group_by(Bookmark.recipe_id)
        .all()
    )

    result = {}

    for recipe_id in recipe_ids:
        result[recipe_id] = {
            "like_count": likes.get(recipe_id, 0),
            "comment_count": comments.get(recipe_id, 0),
            "bookmark_count": bookmarks.get(recipe_id, 0)
        }

    return result


def get_interaction_state_batch(
    db: Session,
    recipes: list[Recipe],
    current_user: User | None
):
    if not current_user:
        return {}

    recipe_ids = [r.id for r in recipes]
    author_ids = list(set(r.user_id for r in recipes))

    liked_recipe_ids = set(
        row[0]
        for row in db.query(RecipeLike.recipe_id)
        .filter(
            RecipeLike.user_id == current_user.id,
            RecipeLike.recipe_id.in_(recipe_ids)
        )
        .all()
    )

    bookmarked_recipe_ids = set(
        row[0]
        for row in db.query(Bookmark.recipe_id)
        .filter(
            Bookmark.user_id == current_user.id,
            Bookmark.recipe_id.in_(recipe_ids)
        )
        .all()
    )

    followed_author_ids = set(
        row[0]
        for row in db.query(Follow.following_id)
        .filter(
            Follow.follower_id == current_user.id,
            Follow.following_id.in_(author_ids)
        )
        .all()
    )

    result = {}

    for recipe in recipes:
        result[recipe.id] = {
            "is_liked": recipe.id in liked_recipe_ids,
            "is_bookmarked": recipe.id in bookmarked_recipe_ids,
            "is_following_author": recipe.user_id in followed_author_ids
        }

    return result


def build_recipe_summary(
    recipe: Recipe,
    counters_data=None,
    interaction_data=None
):
    counters_data = counters_data or {}
    interaction_data = interaction_data or {}

    counters = counters_data.get(
        recipe.id,
        {
            "like_count": 0,
            "comment_count": 0,
            "bookmark_count": 0
        }
    )

    interaction = interaction_data.get(
        recipe.id,
        {
            "is_liked": False,
            "is_bookmarked": False,
            "is_following_author": False
        }
    )

    return RecipeSummaryResponse(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cover_image_url=recipe.cover_image_url,
        cooking_time_minutes=recipe.cooking_time_minutes,
        servings=recipe.servings,
        cooking_cost=recipe.cooking_cost,
        contains_pork=recipe.contains_pork,
        contains_alcohol=recipe.contains_alcohol,
        visibility=recipe.visibility,
        author=UserSummary.model_validate(recipe.author),
        categories=[
            CategoryResponse.model_validate(rc.category)
            for rc in recipe.categories
        ],
        counters=counters,
        interaction_state=interaction,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at
    )


def build_recipe_detail(
    db: Session,
    recipe: Recipe,
    current_user: User | None = None
):
    counters_data = get_recipe_counters_batch(
        db,
        [recipe.id]
    )

    interaction_data = get_interaction_state_batch(
        db,
        [recipe],
        current_user
    )

    summary = build_recipe_summary(
        recipe=recipe,
        counters_data=counters_data,
        interaction_data=interaction_data
    )

    ingredient_groups = []

    for group in sorted(
        recipe.ingredient_groups,
        key=lambda x: x.display_order
    ):
        ingredient_groups.append(
            IngredientGroupResponse(
                id=group.id,
                group_name=group.group_name,
                display_order=group.display_order,
                ingredients=[
                    IngredientResponse(
                        id=ingredient.id,
                        ingredient_text=ingredient.ingredient_text,
                        display_order=ingredient.display_order
                    )
                    for ingredient in sorted(
                        group.ingredients,
                        key=lambda x: x.display_order
                    )
                ]
            )
        )

    steps = []

    for step in sorted(
        recipe.steps,
        key=lambda x: x.step_number
    ):
        steps.append(
            RecipeStepResponse(
                id=step.id,
                step_number=step.step_number,
                instruction_text=step.instruction_text,
                images=[
                    StepImageResponse(
                        id=image.id,
                        image_url=image.image_url,
                        display_order=image.display_order
                    )
                    for image in sorted(
                        step.images,
                        key=lambda x: x.display_order
                    )
                ]
            )
        )

    return RecipeDetailResponse(
        **summary.model_dump(),
        ingredient_groups=ingredient_groups,
        steps=steps
    )


def create_recipe(
    db,
    payload,
    current_user
):
    recipe = Recipe(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        cooking_time_minutes=payload.cooking_time_minutes,
        servings=payload.servings,
        cooking_cost=payload.cooking_cost,
        contains_pork=payload.contains_pork,
        contains_alcohol=payload.contains_alcohol,
        visibility=payload.visibility
    )

    db.add(recipe)
    db.commit()

    recipe = get_recipe_by_id(db, recipe.id)

    counters_data = get_recipe_counters_batch(
        db,
        [recipe.id]
    )

    interaction_data = get_interaction_state_batch(
        db,
        [recipe],
        current_user
    )

    return build_recipe_summary(
        recipe=recipe,
        counters_data=counters_data,
        interaction_data=interaction_data
    )


def update_recipe(
    db,
    recipe_id,
    payload,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.commit()

    recipe = get_recipe_by_id(db, recipe.id)

    counters_data = get_recipe_counters_batch(
        db,
        [recipe.id]
    )

    interaction_data = get_interaction_state_batch(
        db,
        [recipe],
        current_user
    )

    return build_recipe_summary(
        recipe=recipe,
        counters_data=counters_data,
        interaction_data=interaction_data
    )


def delete_recipe(
    db,
    recipe_id,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    recipe.deleted_at = datetime.utcnow()

    db.commit()


def update_recipe_visibility(
    db,
    recipe_id,
    visibility,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    recipe.visibility = visibility

    db.commit()

    recipe = get_recipe_by_id(db, recipe.id)

    counters_data = get_recipe_counters_batch(
        db,
        [recipe.id]
    )

    interaction_data = get_interaction_state_batch(
        db,
        [recipe],
        current_user
    )

    return build_recipe_summary(
        recipe=recipe,
        counters_data=counters_data,
        interaction_data=interaction_data
    )


def assign_recipe_categories(
    db,
    recipe_id,
    payload,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    categories = db.query(Category).filter(
        Category.id.in_(payload.category_ids)
    ).all()

    found_category_ids = {c.id for c in categories}
    requested_category_ids = set(payload.category_ids)

    missing_ids = requested_category_ids - found_category_ids

    if missing_ids:
        raise NotFoundException(
            f"Category not found: {sorted(list(missing_ids))}"
        )

    db.query(RecipeCategory).filter(
        RecipeCategory.recipe_id == recipe.id
    ).delete()

    db.flush()

    db.add_all([
        RecipeCategory(
            recipe_id=recipe.id,
            category_id=category.id
        )
        for category in categories
    ])

    db.commit()

    recipe = get_recipe_by_id(db, recipe.id)

    counters_data = get_recipe_counters_batch(
        db,
        [recipe.id]
    )

    interaction_data = get_interaction_state_batch(
        db,
        [recipe],
        current_user
    )

    return build_recipe_summary(
        recipe=recipe,
        counters_data=counters_data,
        interaction_data=interaction_data
    )


def get_public_recipes(
    db,
    page,
    limit,
    search,
    category_ids,
    contains_pork,
    contains_alcohol,
    max_cooking_time,
    sort_by,
    sort_order,
    current_user=None
):
    query = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.author),
            joinedload(Recipe.categories).joinedload(
                RecipeCategory.category
            )
        )
        .filter(
            Recipe.deleted_at.is_(None),
            Recipe.visibility == "public"
        )
    )

    if search:
        query = query.filter(
            or_(
                Recipe.title.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%")
            )
        )

    if category_ids:
        query = query.join(RecipeCategory).filter(
            RecipeCategory.category_id.in_(category_ids)
        )

    if contains_pork is not None:
        query = query.filter(
            Recipe.contains_pork == contains_pork
        )

    if contains_alcohol is not None:
        query = query.filter(
            Recipe.contains_alcohol == contains_alcohol
        )

    if max_cooking_time is not None:
        query = query.filter(
            Recipe.cooking_time_minutes <= max_cooking_time
        )

    sortable_fields = {
        "created_at": Recipe.created_at,
        "title": Recipe.title,
        "cooking_time_minutes": Recipe.cooking_time_minutes
    }

    sort_column = sortable_fields.get(
        sort_by,
        Recipe.created_at
    )

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = query.count()

    recipes = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    recipe_ids = [r.id for r in recipes]

    counters_data = get_recipe_counters_batch(
        db,
        recipe_ids
    )

    interaction_data = get_interaction_state_batch(
        db,
        recipes,
        current_user
    )

    return PaginatedData(
        items=[
            build_recipe_summary(
                recipe=r,
                counters_data=counters_data,
                interaction_data=interaction_data
            )
            for r in recipes
        ],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total else 1
        )
    )


def get_my_recipes(
    db,
    current_user
):
    recipes = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.author),
            joinedload(Recipe.categories).joinedload(
                RecipeCategory.category
            )
        )
        .filter(
            Recipe.deleted_at.is_(None),
            Recipe.user_id == current_user.id
        )
        .all()
    )

    recipe_ids = [r.id for r in recipes]

    counters_data = get_recipe_counters_batch(
        db,
        recipe_ids
    )

    interaction_data = get_interaction_state_batch(
        db,
        recipes,
        current_user
    )

    return [
        build_recipe_summary(
            recipe=r,
            counters_data=counters_data,
            interaction_data=interaction_data
        )
        for r in recipes
    ]


def get_recipe_detail(
    db,
    recipe_id,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    if recipe.visibility == "private":
        if not current_user or recipe.user_id != current_user.id:
            raise NotFoundException("Recipe not found")

    return build_recipe_detail(
        db=db,
        recipe=recipe,
        current_user=current_user
    )


def upload_recipe_cover(
    db,
    recipe_id,
    file,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_owner(recipe, current_user)

    validate_image_upload(file)

    extension = Path(file.filename).suffix.lower()

    filename = f"{uuid4()}{extension}"

    save_path = Path("app/uploads/recipe_covers") / filename

    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    recipe.cover_image_url = (
        f"{settings.BASE_URL}/uploads/recipe_covers/{filename}"
    )

    db.commit()

    recipe = get_recipe_by_id(db, recipe.id)

    counters_data = get_recipe_counters_batch(
        db,
        [recipe.id]
    )

    interaction_data = get_interaction_state_batch(
        db,
        [recipe],
        current_user
    )

    return build_recipe_summary(
        recipe=recipe,
        counters_data=counters_data,
        interaction_data=interaction_data
    )