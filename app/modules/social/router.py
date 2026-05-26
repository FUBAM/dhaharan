from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user
from app.modules.social.schemas import (
    BookmarkCreateRequest,
    BookmarkNoteUpdateRequest,
    CommentCreateRequest,
    CommentUpdateRequest
)
from app.modules.social.service import (
    bookmark_recipe,
    create_comment,
    delete_comment,
    follow_user,
    get_followers,
    get_following,
    get_my_bookmarks,
    get_recipe_comments,
    like_recipe,
    remove_bookmark,
    unfollow_user,
    unlike_recipe,
    update_bookmark_note,
    update_comment
)
from app.core.dependencies import (
    get_current_user,
    get_optional_current_user
)


router = APIRouter(
    tags=["Social"]
)


@router.post("/api/v1/recipes/{recipe_id}/like")
def like_recipe_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    like_recipe(
        db=db,
        recipe_id=recipe_id,
        current_user=current_user
    )

    return success_response(
        message="Recipe liked successfully"
    )


@router.delete("/api/v1/recipes/{recipe_id}/like")
def unlike_recipe_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    unlike_recipe(
        db=db,
        recipe_id=recipe_id,
        current_user=current_user
    )

    return success_response(
        message="Recipe unliked successfully"
    )


@router.post("/api/v1/recipes/{recipe_id}/bookmark")
def bookmark_recipe_endpoint(
    recipe_id: int,
    payload: BookmarkCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bookmark = bookmark_recipe(
        db=db,
        recipe_id=recipe_id,
        personal_note=payload.personal_note,
        current_user=current_user
    )

    return success_response(
        message="Recipe bookmarked successfully",
        data=bookmark
    )


@router.patch("/api/v1/bookmarks/{bookmark_id}/note")
def update_bookmark_note_endpoint(
    bookmark_id: int,
    payload: BookmarkNoteUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bookmark = update_bookmark_note(
        db=db,
        bookmark_id=bookmark_id,
        personal_note=payload.personal_note,
        current_user=current_user
    )

    return success_response(
        message="Bookmark note updated successfully",
        data=bookmark
    )


@router.delete("/api/v1/recipes/{recipe_id}/bookmark")
def remove_bookmark_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    remove_bookmark(
        db=db,
        recipe_id=recipe_id,
        current_user=current_user
    )

    return success_response(
        message="Bookmark removed successfully"
    )


@router.get("/api/v1/me/bookmarks")
def my_bookmarks_endpoint(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bookmarks = get_my_bookmarks(
        db=db,
        current_user=current_user,
        page=page,
        limit=limit
    )

    return success_response(
        message="Bookmarks fetched successfully",
        data=bookmarks
    )


@router.get("/api/v1/recipes/{recipe_id}/comments")
def recipe_comments_endpoint(
    recipe_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user)
):
    comments = get_recipe_comments(
        db=db,
        recipe_id=recipe_id,
        page=page,
        limit=limit,
        current_user=current_user
    )

    return success_response(
        message="Comments fetched successfully",
        data=comments
    )


@router.post("/api/v1/recipes/{recipe_id}/comments")
def create_comment_endpoint(
    recipe_id: int,
    payload: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = create_comment(
        db=db,
        recipe_id=recipe_id,
        content=payload.content,
        current_user=current_user
    )

    return success_response(
        message="Comment created successfully",
        data=comment
    )


@router.patch("/api/v1/comments/{comment_id}")
def update_comment_endpoint(
    comment_id: int,
    payload: CommentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = update_comment(
        db=db,
        comment_id=comment_id,
        content=payload.content,
        current_user=current_user
    )

    return success_response(
        message="Comment updated successfully",
        data=comment
    )


@router.delete("/api/v1/comments/{comment_id}")
def delete_comment_endpoint(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )

    return success_response(
        message="Comment deleted successfully"
    )


@router.post("/api/v1/users/{user_id}/follow")
def follow_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    follow_user(
        db=db,
        user_id=user_id,
        current_user=current_user
    )

    return success_response(
        message="User followed successfully"
    )


@router.delete("/api/v1/users/{user_id}/follow")
def unfollow_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    unfollow_user(
        db=db,
        user_id=user_id,
        current_user=current_user
    )

    return success_response(
        message="User unfollowed successfully"
    )


@router.get("/api/v1/users/{user_id}/followers")
def followers_endpoint(
    user_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    followers = get_followers(
        db=db,
        user_id=user_id,
        page=page,
        limit=limit
    )

    return success_response(
        message="Followers fetched successfully",
        data=followers
    )


@router.get("/api/v1/users/{user_id}/following")
def following_endpoint(
    user_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    following = get_following(
        db=db,
        user_id=user_id,
        page=page,
        limit=limit
    )

    return success_response(
        message="Following fetched successfully",
        data=following
    )