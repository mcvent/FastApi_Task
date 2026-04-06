from contextlib import contextmanager
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


class Database:
    def __init__(self):
        current_file = Path(__file__).resolve()  # .../fastapi_app/src/infrastructure/sqlite/database.py
        project_root = current_file.parent.parent.parent.parent.parent

        db_path = project_root / 'db.sqlite3'

        self._db_url = f"sqlite:///{db_path}"
        self._engine = create_engine(self._db_url, echo=False)  # echo=True для отладки

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