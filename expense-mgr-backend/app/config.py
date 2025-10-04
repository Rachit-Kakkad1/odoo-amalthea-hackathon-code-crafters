import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .deps import get_db
from .crud import get_user_by_username, update_user_reset_token, update_user_password
from .schemas import User
import secrets
import string

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Hash password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Authenticate user
async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | bool:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Create access token
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Create reset token
def create_reset_token(mobile_number: str, expires_delta: timedelta = None) -> str:
    to_encode = {"sub": mobile_number, "type": "reset"}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Verify reset token
def verify_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        mobile_number: str = payload.get("sub")
        if mobile_number is None or payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        return mobile_number
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

# Send email
async def send_email(to_email: str, subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)

# Generate random password
def generate_random_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user