# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String(255), unique=True, nullable=False)
    nickname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    profile_img = Column(String(255), nullable=True)  # 프로필 이미지 URL
    continuous_days = Column(Integer, default=0)
    
    reflections = relationship('Reflection', back_populates='user')
    commits = relationship('Commit', back_populates='user')
    images = relationship('Image', back_populates='user')

class Reflection(Base):
    __tablename__ = 'reflections'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='reflections')
    images = relationship('Image', back_populates='reflection')

class Commit(Base):
    __tablename__ = 'commits'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    
    user = relationship('User', back_populates='commits')

class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, index=True)
    reflection_id = Column(Integer, ForeignKey('reflections.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='images')
    reflection = relationship('Reflection', back_populates='images')
