from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nickname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    continuous_days = Column(Integer, nullable=True)
    profile_img = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    reflections = relationship("Reflection", back_populates="user")
    images = relationship("Image", back_populates="user")

class Reflection(Base):
    __tablename__ = "reflection"
    
    reflection_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    todo = Column(String(255), nullable=False)
    resolution = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="reflections")
    images = relationship("Image", back_populates="reflection")

class Image(Base):
    __tablename__ = "image"
    
    image_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reflection_id = Column(Integer, ForeignKey("reflection.reflection_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    reflection = relationship("Reflection", back_populates="images")
    user = relationship("User", back_populates="images")