# models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip = Column(String)
    method = Column(String)
    url = Column(String)
    user_agent = Column(String)
    referer = Column(String)
    accept_language = Column(String)
    content_type = Column(String)