from fastapi import FastAPI
from app.routes import users, posts
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/users")
app.include_router(posts.router, prefix="/posts")
