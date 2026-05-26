from sqlalchemy.orm import Session

from app.modules.categories.models import Category


def get_all_categories(db: Session) -> list[Category]:
    return (
        db.query(Category)
        .order_by(Category.name.asc())
        .all()
    )