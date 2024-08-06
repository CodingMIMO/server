from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.models import Reflection, Image, User
from app.schemas import ReflectionCreate, ReflectionResponse
from ai.model import sampling  # AI 모델 호출 함수
from app.dependencies import get_db 
import os
from app.schemas import ReflectionWithImageResponse, ImageResponse, SetProfileImageRequest, SetProfileImageResponse
from datetime import datetime                              


router = APIRouter(prefix="/api/v1")

## 회고 작성 API 
## 회고를 작성해 요청하면 이미지를 만들어 반환한다.
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

        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

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

## 해당 사진을 프로필 이미지로 설정하는 API 
@router.post("/reflections/img", response_model=SetProfileImageResponse, status_code=status.HTTP_200_OK)
def set_profile_image(
    request: SetProfileImageRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    try:
        # Reflection ID로 이미지를 찾음
        db_image = db.query(Image).filter(Image.reflection_id == request.reflection_id).first()
        if db_image is None:
            raise HTTPException(status_code=404, detail="해당 회고에 연결된 이미지를 찾을 수 없습니다.")

        # 이미지와 연결된 사용자 찾기
        user = db.query(User).filter(User.id == db_image.user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 사용자 프로필 이미지 업데이트
        user.profile_img = db_image.image_url
        db.commit()

        return SetProfileImageResponse(
            status=200,
            message="성공"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="실패")
