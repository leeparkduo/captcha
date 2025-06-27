from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, func
from .database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    topic = Column(String, nullable=False)
    topic_data_idx = Column(Integer, nullable=False)
    prompt = Column(String, nullable=False)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    ground_truth = Column(String, nullable=False)
    expected_bias = Column(String, nullable=False)
    user_masks = Column(JSON, nullable=True)
    user_answer = Column(String, nullable=True)
    passed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())