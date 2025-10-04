from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from . import database, schemas
from .main import oauth2_scheme, settings, get_db

def get_user_by_email(db: Session, email: str):
    """
    READ operation: Retrieves a single user from the database
    by their email address.
    """
    return db.query(database.User).filter(database.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """
    CREATE operation: Creates a new user in the database.
    - It takes the data from the UserCreate schema.
    - It uses the hashed password provided by the security logic.
    """
    db_user = database.User(
        name=user.name,
        email=user.email,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: database.User, hashed_password: str):
    """
    UPDATE operation: Updates an existing user's password in the database.
    """
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user

# This is a special READ function used for security.
# It reads the user based on the JWT token provided in an API request.
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user