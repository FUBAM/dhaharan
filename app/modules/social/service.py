from math import ceil

from app.common.schemas import (
    PaginationMeta,
    PaginatedData
)

from sqlalchemy.orm import Session, joinedload

from app.common.schemas import (
    CounterResponse,
    InteractionStateResponse,
    UserSummary
)
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException
)
from app.modules.recipes.models import Recipe
from app.modules.social.models import (
    Bookmark,
    Comment,
    Follow,
    RecipeLike
)
from app.modules.social.schemas import (
    BookmarkResponse,
    CommentResponse,
    FollowUserResponse
)
from app.modules.users.models import User


def get_recipe_by_id(
    db: Session,
    recipe_id: int
) -> Recipe | None:
    return (
        db.query(Recipe)
        .filter(
            Recipe.id == recipe_id,
            Recipe.deleted_at.is_(None)
        )
        .first()
    )

def validate_recipe_access_for_interaction(
    recipe: Recipe,
    current_user: User
):
    if recipe.visibility == "private":
        if recipe.user_id != current_user.id:
            raise NotFoundException("Recipe not found")

def get_user_by_id(
    db: Session,
    user_id: int
) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def like_recipe(db, recipe_id, current_user):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    validate_recipe_access_for_interaction(
        recipe,
        current_user
    )

    existing = db.query(RecipeLike).filter(
        RecipeLike.user_id == current_user.id,
        RecipeLike.recipe_id == recipe.id
    ).first()

    if existing:
        raise BadRequestException("Recipe already liked")

    db.add(
        RecipeLike(
            user_id=current_user.id,
            recipe_id=recipe.id
        )
    )

    db.commit()


def unlike_recipe(db, recipe_id, current_user):
    like = db.query(RecipeLike).filter(
        RecipeLike.user_id == current_user.id,
        RecipeLike.recipe_id == recipe_id
    ).first()

    if not like:
        raise NotFoundException("Like not found")

    db.delete(like)
    db.commit()


def bookmark_recipe(
    db,
    recipe_id,
    personal_note,
    current_user
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")
    
    validate_recipe_access_for_interaction(
        recipe,
        current_user
    )

    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.recipe_id == recipe.id
    ).first()

    if existing:
        raise BadRequestException("Recipe already bookmarked")

    bookmark = Bookmark(
        user_id=current_user.id,
        recipe_id=recipe.id,
        personal_note=personal_note
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        recipe_id=bookmark.recipe_id,
        personal_note=bookmark.personal_note,
        created_at=bookmark.created_at
    )


def update_bookmark_note(
    db,
    bookmark_id,
    personal_note,
    current_user
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id
    ).first()

    if not bookmark:
        raise NotFoundException("Bookmark not found")

    if bookmark.user_id != current_user.id:
        raise ForbiddenException("Not your bookmark")

    bookmark.personal_note = personal_note

    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        recipe_id=bookmark.recipe_id,
        personal_note=bookmark.personal_note,
        created_at=bookmark.created_at
    )


def remove_bookmark(
    db,
    recipe_id,
    current_user
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.recipe_id == recipe_id
    ).first()

    if not bookmark:
        raise NotFoundException("Bookmark not found")

    db.delete(bookmark)
    db.commit()


def get_my_bookmarks(
    db,
    current_user,
    page,
    limit
):
    query = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).order_by(
        Bookmark.created_at.desc()
    )

    total = query.count()

    bookmarks = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedData(
        items=[
            BookmarkResponse(
                id=b.id,
                recipe_id=b.recipe_id,
                personal_note=b.personal_note,
                created_at=b.created_at
            )
            for b in bookmarks
        ],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total else 1
        )
    )


def get_recipe_comments(
    db,
    recipe_id,
    page,
    limit,
    current_user=None
):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")

    if recipe.visibility == "private":
        if not current_user or recipe.user_id != current_user.id:
            raise NotFoundException("Recipe not found")

    query = (
        db.query(Comment)
        .options(
            joinedload(Comment.user)
        )
        .filter(Comment.recipe_id == recipe_id)
        .order_by(Comment.created_at.asc())
    )

    total = query.count()

    comments = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedData(
        items=[
            CommentResponse(
                id=c.id,
                content=c.content,
                author=UserSummary.model_validate(c.user),
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in comments
        ],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total else 1
        )
    )


def create_comment(db, recipe_id, content, current_user):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise NotFoundException("Recipe not found")
    
    validate_recipe_access_for_interaction(
        recipe,
        current_user
    )

    comment = Comment(
        user_id=current_user.id,
        recipe_id=recipe.id,
        content=content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        author=UserSummary.model_validate(current_user),
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


def update_comment(db, comment_id, content, current_user):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise NotFoundException("Comment not found")

    if comment.user_id != current_user.id:
        raise ForbiddenException("Not your comment")

    comment.content = content

    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        author=UserSummary.model_validate(current_user),
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


def delete_comment(db, comment_id, current_user):
    comment = db.query(Comment).options(
        joinedload(Comment.recipe)
    ).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise NotFoundException("Comment not found")

    if (
        comment.user_id != current_user.id
        and comment.recipe.user_id != current_user.id
    ):
        raise ForbiddenException("Not allowed")

    db.delete(comment)
    db.commit()


def follow_user(db, user_id, current_user):
    if user_id == current_user.id:
        raise BadRequestException("Cannot follow yourself")

    target = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

    if not target:
        raise NotFoundException("User not found")

    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if existing:
        raise BadRequestException("Already following")

    db.add(
        Follow(
            follower_id=current_user.id,
            following_id=user_id
        )
    )

    db.commit()


def unfollow_user(db, user_id, current_user):
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()

    if not follow:
        raise NotFoundException("Follow not found")

    db.delete(follow)
    db.commit()


def get_followers(
    db,
    user_id,
    page,
    limit
):
    target = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

    if not target:
        raise NotFoundException("User not found")

    query = (
        db.query(Follow)
        .options(
            joinedload(Follow.follower)
        )
        .filter(Follow.following_id == user_id)
    )

    total = query.count()

    rows = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedData(
        items=[
            FollowUserResponse.model_validate(row.follower)
            for row in rows
        ],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total else 1
        )
    )


def get_following(
    db,
    user_id,
    page,
    limit
):
    target = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

    if not target:
        raise NotFoundException("User not found")

    query = (
        db.query(Follow)
        .options(
            joinedload(Follow.following)
        )
        .filter(Follow.follower_id == user_id)
    )

    total = query.count()

    rows = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedData(
        items=[
            FollowUserResponse.model_validate(row.following)
            for row in rows
        ],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total else 1
        )
    )


def get_recipe_counters(db, recipe_id):
    return CounterResponse(
        like_count=db.query(RecipeLike).filter(
            RecipeLike.recipe_id == recipe_id
        ).count(),
        comment_count=db.query(Comment).filter(
            Comment.recipe_id == recipe_id
        ).count(),
        bookmark_count=db.query(Bookmark).filter(
            Bookmark.recipe_id == recipe_id
        ).count()
    )


def get_interaction_state(
    db,
    recipe,
    current_user
):
    if not current_user:
        return InteractionStateResponse(
            is_liked=False,
            is_bookmarked=False,
            is_following_author=False
        )

    return InteractionStateResponse(
        is_liked=db.query(RecipeLike).filter(
            RecipeLike.user_id == current_user.id,
            RecipeLike.recipe_id == recipe.id
        ).first() is not None,

        is_bookmarked=db.query(Bookmark).filter(
            Bookmark.user_id == current_user.id,
            Bookmark.recipe_id == recipe.id
        ).first() is not None,

        is_following_author=db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == recipe.user_id
        ).first() is not None
    )