"""
Developed by Aindriya Barua in December, 2023
"""

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
import jwt
import secrets
from typing import Optional

import pickle
from pydantic import BaseModel
from sklearn.ensemble import RandomForestClassifier
import fasttext
import logging

import text_preprocessor
import constants


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = constants.ALGORITHM

DATABASE_URL = constants.DATABASE_URL
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String)
    request_count = Column(Integer, default=0)  # New column for request count

# Create the SQLite database engine
engine = create_engine(DATABASE_URL , connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create a new session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# Allow all origins (not recommended for production)
# Replace "*" with a list of allowed origins if needed
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the HTTP methods that are allowed
    allow_headers=["*"],  # You can specify the HTTP headers that are allowed
)


# OAuth2PasswordBearer for handling token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Content(BaseModel):
    text: str

ft_model = fasttext.load_model(constants.FT_MODEL)
with open(constants.HATE_DETECTION_MODEL, "rb") as f:
    rfc = pickle.load(f)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
    
# Function to get the current user based on the provided token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_data = decode_access_token(token)
        if user_data:
            user = db.query(User).filter(User.username == user_data["sub"]).first()
            print("user::::", user)
            if user:
                return user
    except Exception as e:
        print(f"Error decoding access token: {e}")
    raise credentials_exception

# Function to verify user credentials using the database
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
        return user

# Function to create an access token
def create_access_token(data: dict):
    return {"access_token": jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}


# Registration endpoint
@app.post("/register", response_model=None)
async def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        logger.info('Registration endpoint accessed')

        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.warning(f"Registration failed. Username '{username}' already exists.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        db_user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User registered successfully: {username}")
        return db_user

    except Exception as e:
        logger.error(f"Error in registration endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in registration",
        )


# Index endpoint
@app.get('/')
def index():
    logger.info('Index endpoint accessed')
    return {'message': 'This is the homepage of the API '}


# Prediction endpoint with user authentication
@app.post('/prediction')
def detect_hate(data: Content, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        logger.info('Prediction endpoint accessed')
        
        received = data.dict()
        text = received['text']
        logger.info(f'Received text for prediction: {text}')

        preprocessed_text = text_preprocessor.preprocess_main(text)
        logger.info(f'Preprocessed text: {preprocessed_text}')

        vec = ft_model.get_sentence_vector(str(preprocessed_text))
        pred = rfc.predict([vec]).tolist()[0]

        try:
            # Increment the request_count for the user
            current_user.request_count += 1
            db.commit()  # Save the updated user to the database
            logger.info(f'Request count incremented for user: {current_user.username}')
        except Exception as e:
            logger.error(f"Error updating request count: {e}", exc_info=True)

        response = {'prediction': pred}
        logger.info(f'Response sent: {response}')

        return response

    except Exception as e:
        logger.error(f'Error in prediction endpoint: {e}', exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Error in prediction')


# Token endpoint for user authentication
@app.post("/token", response_model=dict)
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        logger.info('Token (Login) endpoint accessed')
        user = authenticate_user(db, form_data.username, form_data.password)

        if user:
            token_data = {"sub": form_data.username}
            logger.info(f"User {form_data.username} authenticated successfully. Generating access token.")
            return create_access_token(token_data)
        else:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Request count endpoint
@app.get('/user/{username}/request_count')
def get_user_request_count(username: str, db: Session = Depends(get_db)):
    try:
        logger.info(f'Request per user endpoint accessed for user: {username}')
        user = db.query(User).filter(User.username == username).first()

        if not user:
            logger.warning(f"User {username} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found",
            )

        logger.info(f"Request count retrieved successfully for user: {username}")
        return {'username': user.username, 'request_count': user.request_count}

    except Exception as e:
        logger.error(f"Error retrieving request count: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in retrieving request count",
        )

    
if __name__ == '__main__':
    uvicorn.run(app, debug=True)
