from sqlalchemy import create_engine
import json


class DBClient:
    def __init__(self):
        with open('credentials/db_credentials.json', 'r') as file:
            db_credentials: dict = json.load(file)
        self.db_name = db_credentials.get('dbname')
        self.user = db_credentials.get('user')
        self.password = db_credentials.get('password')

    def create_sql_alchemy_engine(self):
        db_engine = create_engine(f"postgresql://{self.user}:{self.password}@localhost/{self.db_name}")
        return db_engine
