from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


class Database:
    def __init__(self):
        self._db_url = "sqlite:///D:/Univercity_2course/2 term/FastApi_Tasks/FastApi_Task3-4/db.sqlite3"
        self._engine = create_engine(self._db_url)

    @contextmanager
    def session(self):
        connection = self._engine.connect()

        Session = sessionmaker(bind=self._engine)
        session = Session()

        try:
            yield session
            session.commit()
            connection.close()
        except Exception:
            session.rollback()
            raise


database = Database()
Base = declarative_base()