# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:00000000@localhost/mimo"
# mysqlclient를 사용하는 경우 URL은 다음과 같습니다:
# SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://username:password@localhost/mydatabase"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
