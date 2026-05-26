from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IngredientGroup(Base):
    __tablename__ = "recipe_ingredient_groups"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )

    group_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    recipe = relationship(
        "Recipe",
        back_populates="ingredient_groups"
    )

    ingredients = relationship(
        "Ingredient",
        back_populates="group",
        cascade="all, delete-orphan"
    )


class Ingredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    ingredient_group_id: Mapped[int] = mapped_column(
        ForeignKey("recipe_ingredient_groups.id", ondelete="CASCADE"),
        nullable=False
    )

    ingredient_text: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    group = relationship(
        "IngredientGroup",
        back_populates="ingredients"
    )