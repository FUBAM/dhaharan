from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.common.responses import error_response
from app.core.config import settings
from app.core.exceptions import AppException

# model registration
from app.modules.users.models import User
from app.modules.categories.models import Category
from app.modules.recipes.models import Recipe, RecipeCategory
from app.modules.ingredients.models import IngredientGroup, Ingredient
from app.modules.steps.models import RecipeStep, RecipeStepImage
from app.modules.social.models import (
    RecipeLike,
    Bookmark,
    Comment,
    Follow
)

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as user_router
from app.modules.categories.router import router as category_router
from app.modules.recipes.router import router as recipe_router
from app.modules.ingredients.router import router as ingredient_router
from app.modules.steps.router import router as step_router
from app.modules.social.router import router as social_router


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)


UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

Path("app/uploads/profiles").mkdir(parents=True, exist_ok=True)
Path("app/uploads/recipe_covers").mkdir(parents=True, exist_ok=True)
Path("app/uploads/recipe_steps").mkdir(parents=True, exist_ok=True)


app.mount(
    "/uploads",
    StaticFiles(directory="app/uploads"),
    name="uploads"
)


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message
        ).model_dump()
    )


@app.get("/")
def root():
    return {
        "message": "Dhaharan API is running"
    }


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(recipe_router)
app.include_router(ingredient_router)
app.include_router(step_router)
app.include_router(social_router)