from fastapi import FastAPI
from .database import engine
from .models import Base
from .api.domain import reflection
from .api.domain import user
from fastapi.staticfiles import StaticFiles
# from .api.domain import user, reflection
# from database import engine
# from models import Base

app = FastAPI()

#테이블 자동 생성 
Base.metadata.create_all(bind=engine)

app.include_router(reflection.router)
app.include_router(user.router)
app.mount("/images", StaticFiles(directory="app/images"), name="images")
