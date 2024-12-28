from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Post, Like, Comment, Follow
from app.schemas import PostCreate, PostResponse, CommentBase
from app.auth.jwt_handler import verify_access_token

router = APIRouter()


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    current_user_id = token.get("sub")
    db_post = Post(**post.dict(), user_id=current_user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return db_post


@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    current_user_id = token.get("sub")
    like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user_id).first()
    if like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked this post")
    new_like = Like(post_id=post_id, user_id=current_user_id)
    db.add(new_like)
    db.commit()
    return {"message": "Post liked successfully"}


@router.get("/{post_id}/likes")
def get_post_likes(post_id: int, db: Session = Depends(get_db)):
    likes = db.query(Like).filter(Like.post_id == post_id).all()
    return {"count": len(likes), "likes": [{"user_id": like.user_id} for like in likes]}


@router.post("/{post_id}/comment")
def comment_on_post(post_id: int, comment: CommentBase, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    current_user_id = token.get("sub")
    new_comment = Comment(post_id=post_id, user_id=current_user_id, content=comment.content)
    db.add(new_comment)
    db.commit()
    return {"message": "Comment added successfully"}


@router.get("/{post_id}/comments")
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return {"count": len(comments), "comments": [{"user_id": comment.user_id, "content": comment.content} for comment in comments]}


@router.get("/feed")
def get_user_feed(page: int = 1, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    current_user_id = token.get("sub")
    following = db.query(Follow.following_id).filter(Follow.follower_id == current_user_id).subquery()
    feed = db.query(Post).filter(Post.user_id.in_(following)).order_by(desc(Post.created_at)).offset((page - 1) * limit).limit(limit).all()
    return feed
