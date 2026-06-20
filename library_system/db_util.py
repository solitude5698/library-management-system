from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config
import urllib.parse

current_config = config['default']

config_dict = current_config.DB_CONFIG
server = config_dict['server']
database = config_dict['database']
driver = config_dict['driver']
trusted_connection = config_dict.get('trusted_connection', 'yes')

params = urllib.parse.quote_plus(
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection={trusted_connection};"
    "TrustServerCertificate=yes;"
)

connection_string = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def get_session():
    return Session()

def init_db():
    Base.metadata.create_all(engine)

def close_session(session):
    if session:
        session.close()
