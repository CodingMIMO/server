from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import User as DbUser  # SQLAlchemy User 모델
from app.dependencies import get_db 
from app.schemas import Token, Login, UserResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
router = APIRouter(prefix="/api/v1")

@router.post("/login", response_model=Token)
def login(login_data: Login, db: Session = Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user_id": user.user_id,   # user_id 반환
        "nickname": user.nickname  # nickname 반환
    }

@router.post("/register", response_model=Token)
def register(nickname: str, email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.email == email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(password)
    new_user = DbUser(email=email, hashed_password=hashed_password, nickname=nickname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user_id": new_user.user_id,   # user_id 반환
        "nickname": new_user.nickname  # nickname 반환
    }