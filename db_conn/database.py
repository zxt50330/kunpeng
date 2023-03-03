from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import threading


class DatabaseConnection(object):
    """
    A singleton class for database connection
    """
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                engine = create_engine('postgresql://:@localhost:5432/kunpeng', poolclass=QueuePool)
                Session = sessionmaker(bind=engine)
                cls._instance = super().__new__(cls)
                cls._instance.Session = scoped_session(Session)
        return cls._instance

    def get_session(self):
        """
        Returns a session object from the connection pool
        """
        return self.Session()


db = DatabaseConnection()
session = db.get_session()
