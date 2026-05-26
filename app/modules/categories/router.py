from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.common.schemas import CategoryResponse
from app.core.database import get_db
from app.modules.categories.service import get_all_categories


router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"]
)


@router.get("")
def list_categories(
    db: Session = Depends(get_db)
):
    categories = get_all_categories(db)

    data = [
        CategoryResponse.model_validate(category)
        for category in categories
    ]

    return success_response(
        message="Categories fetched successfully",
        data=data
    )