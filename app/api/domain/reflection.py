from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.models import Reflection, Image, User
from app.schemas import ReflectionCreate, ReflectionResponse
from ai.model import sampling  # AI 모델 호출 함수
from app.dependencies import get_db 
import os
from uuid import uuid4
from app.schemas import ReflectionWithImageResponse, ImageResponse    
from datetime import datetime                              


router = APIRouter(prefix="/api/v1")

@router.post("/reflections", response_model=ReflectionWithImageResponse, status_code=status.HTTP_201_CREATED)
def create_reflection(
    reflection: ReflectionCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    try:
        # 1. 사용자 조회
        user = db.query(User).filter(User.id == reflection.user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. 회고를 데이터베이스에 저장
        db_reflection = Reflection(
            user_id=reflection.user_id,
            content=reflection.content,
        )
        db.add(db_reflection)
        db.commit()
        db.refresh(db_reflection)

        # 3. 회고를 프롬프트로 사용하여 이미지 생성
        prompt = [reflection.content]
        images = sampling(prompt)

         # 이미지 생성 실패 시 처리
        if images is None or len(images) == 0:
            raise HTTPException(status_code=500, detail="이미지 생성에 실패했습니다.")
        
        # 현재 날짜를 문자열로 변환
        current_date = datetime.now().strftime("%Y%m%d")

        # 이미지 파일 이름을 '유저아이디_날짜.png' 형식으로 생성
        file_name = f"{reflection.user_id}_{current_date}.png"
        file_path = os.path.join("images", file_name)
        images[0].save(file_path)

        # 5. 이미지 정보를 데이터베이스에 저장
        db_image = Image(
            reflection_id=db_reflection.id,
            user_id=reflection.user_id,
            image_url=f"/images/{file_name}",  # URL 경로 설정
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        # 최종 응답 반환
        return ReflectionWithImageResponse(
            reflection=ReflectionResponse(
                reflection_id=db_reflection.id,
                content=db_reflection.content,
                created_at=db_reflection.created_at
            ),
            image=ImageResponse(
                image_id=db_image.id,
                image_url=db_image.image_url,
                created_at=db_image.created_at
            )
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="실패")