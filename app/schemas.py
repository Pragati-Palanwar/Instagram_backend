from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    caption: Optional[str]
    image_url: str
    background_music_url: Optional[str]
    category: Optional[str]

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str

class LikeBase(BaseModel):
    user_id: int
    post_id: int
