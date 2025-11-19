from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(768), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending")  # pending, success, failed, blocked
    depth = Column(Integer, default=0)
    domain = Column(String(255))
    fetched_at = Column(DateTime, nullable=True)
    title = Column(Text, nullable=True)
    error = Column(Text, nullable=True)