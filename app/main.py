from fastapi import FastAPI
from .database import engine
from .models import Base
from app.api.domain import reflection
from fastapi.staticfiles import StaticFiles
# from .api.domain import user, reflection
# from database import engine
# from models import Base

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}

#테이블 자동 생성 
Base.metadata.create_all(bind=engine)

app.include_router(reflection.router)
app.mount("/images", StaticFiles(directory="app/images"), name="images")
# app.include_router(user.router)
# app.include_router(reflection.router)

# def create_tables():
#     Base.metadata.create_all(bind=engine)

# if __name__ == "__main__":