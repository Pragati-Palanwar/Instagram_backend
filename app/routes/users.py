from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.database import get_db
from app.models import User, Follow
from app.schemas import UserCreate, UserResponse
from app.auth.jwt_handler import create_access_token, verify_access_token
from app.config import SECRET_KEY, ALGORITHM

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user or not pwd_context.verify(password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.post("/follow/{user_id}")
def follow_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    current_user_id = token.get("sub")
    if current_user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
    follow_entry = Follow(follower_id=current_user_id, following_id=user_id)
    db.add(follow_entry)
    db.commit()
    return {"message": f"You are now following user {user_id}"}


@router.post("/unfollow/{user_id}")
def unfollow_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(verify_access_token)):
    current_user_id = token.get("sub")
    follow_entry = db.query(Follow).filter(Follow.follower_id == current_user_id, Follow.following_id == user_id).first()
    if not follow_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not following this user")
    db.delete(follow_entry)
    db.commit()
    return {"message": f"You have unfollowed user {user_id}"}
