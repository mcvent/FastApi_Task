from contextlib import contextmanager
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.core.config import settings

class Database:
    def __init__(self):
        self._db_url = settings.DATABASE_URL
        self._engine = create_engine(self._db_url, echo=False)

    @contextmanager
    def session(self):
        Session = sessionmaker(bind=self._engine)
        session = Session()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


database = Database()
Base = declarative_base()