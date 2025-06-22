from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, func
from .database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    question = Column(String, nullable=False)
    ground_truth = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer)
    user_masks = Column(JSON)
    user_answer = Column(String, nullable=False)
    passed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
