from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    instruction_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    recipe = relationship(
        "Recipe",
        back_populates="steps"
    )

    images = relationship(
        "RecipeStepImage",
        back_populates="step",
        cascade="all, delete-orphan"
    )


class RecipeStepImage(Base):
    __tablename__ = "recipe_step_images"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    recipe_step_id: Mapped[int] = mapped_column(
        ForeignKey("recipe_steps.id", ondelete="CASCADE"),
        nullable=False
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    step = relationship(
        "RecipeStep",
        back_populates="images"
    )