from sqlalchemy import (
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.enums import VisibilityEnum
from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    cooking_time_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    servings: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    cooking_cost: Mapped[float] = mapped_column(
        DECIMAL(12, 2),
        nullable=False
    )

    contains_pork: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )

    contains_alcohol: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )

    visibility: Mapped[VisibilityEnum] = mapped_column(
        Enum(VisibilityEnum),
        nullable=False,
        default=VisibilityEnum.private
    )

    cover_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    deleted_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    author = relationship(
        "User",
        back_populates="recipes"
    )

    categories = relationship(
        "RecipeCategory",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    ingredient_groups = relationship(
        "IngredientGroup",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    steps = relationship(
        "RecipeStep",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )


class RecipeCategory(Base):
    __tablename__ = "recipe_categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False
    )

    recipe = relationship(
        "Recipe",
        back_populates="categories"
    )

    category = relationship("Category")