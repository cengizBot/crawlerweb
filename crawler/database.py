from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import os
from .models import Page
from .models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://crawler:crawler@localhost:3306/crawler_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = scoped_session(sessionmaker(bind=engine))

def init_db():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def save_page(url: str, domain: str, status: str):
    """Sauvegarde une page dans la base de données."""
    with get_db() as db:
        page = db.query(Page).filter(Page.url == url).first()
        if not page:
            page = Page(url=url, domain=domain, status=status)
            db.add(page)
        else:
            page.status = status
        db.commit()