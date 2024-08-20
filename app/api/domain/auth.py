from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import User as DbUser  # SQLAlchemy User 모델
from app.dependencies import get_db 
from app.schemas import UserResponse   

router = APIRouter(prefix="/api/v1")

load_dotenv()

# OAuth 설정
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_params=None,
    access_token_params=None,
    redirect_uri='http://localhost:8000/api/v1/auth/google/callback',
    client_kwargs={'scope': 'openid email profile'},
)

# Pydantic 모델 정의 (Google에서 받은 사용자 정보를 담기 위해 사용)
class OAuthUser(BaseModel):
    id: str
    email: str
    name: str

# 인가 코드를 클라이언트로부터 받는 API
@router.post("/auth/google")
async def exchange_code_for_token(code: str = Body(...), db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(code=code)
        user_info = await oauth.google.parse_id_token(token)
        oauth_user = OAuthUser(
            id=user_info['sub'],
            email=user_info['email'],
            name=user_info['name']
        )
        
        # DB에 유저 정보 저장 또는 업데이트
        db_user = db.query(DbUser).filter(DbUser.email == oauth_user.email).first()
        if not db_user:
            db_user = DbUser(
                email=oauth_user.email,
                nickname=oauth_user.name,
                created_at=datetime.utcnow(),
                continuous_days=0  # 예시로 설정, 필요에 따라 수정
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        return UserResponse(
            id=db_user.user_id,
            github_id=db_user.github_id,
            nickname=db_user.nickname,
            email=db_user.email,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google login failed")
