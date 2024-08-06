from pydantic import BaseModel
from datetime import datetime

class ReflectionCreate(BaseModel):
    user_id: int
    content: str

class ReflectionResponse(BaseModel):
    reflection_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2 대응

class ImageResponse(BaseModel):
    image_id: int
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2 대응

class ReflectionWithImageResponse(BaseModel):
    reflection: ReflectionResponse
    image: ImageResponse

    class Config:
        from_attributes = True  # Pydantic V2 대응

class UserBase(BaseModel):
    id: int
    github_id: str
    nickname: str
    email: str
    profile_img: str = None
    continuous_days: int = 0

    class Config:
        from_attributes = True  # Pydantic V2 설정

## 프로필 이미지로 등록 
class SetProfileImageRequest(BaseModel):
    reflection_id: int

class SetProfileImageResponse(BaseModel):
    status: int
    message: str
