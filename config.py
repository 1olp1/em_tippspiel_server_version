from flask import Flask
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["DEBUG"] = True
Session(app)

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}'.format(
    username=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    hostname=os.getenv('DB_HOSTNAME'),
    databasename=os.getenv('DB_DATABASE')
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280  # Setting pool recycle to 280 seconds
app.config["SQLALCHEMY_POOL_TIMEOUT"] = 30   # Timeout for getting a connection from the pool
app.config["SQLALCHEMY_POOL_SIZE"] = 10      # Number of connections to keep in the pool
app.config["SQLALCHEMY_MAX_OVERFLOW"] = 20   # Allow extra connections to be created above pool size

# Create SQLAlchemy engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI, poolclass=QueuePool)
SessionFactory = sessionmaker(bind=engine)
session_db = scoped_session(SessionFactory)

def get_db_session():
    return session_db()
