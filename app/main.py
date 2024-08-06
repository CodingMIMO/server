from fastapi import FastAPI
from .database import engine
from .models import Base
# from .api.domain import user, reflection
# from database import engine
# from models import Base

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}

Base.metadata.create_all(bind=engine)
# app.include_router(user.router)
# app.include_router(reflection.router)

# def create_tables():
#     Base.metadata.create_all(bind=engine)

# if __name__ == "__main__":