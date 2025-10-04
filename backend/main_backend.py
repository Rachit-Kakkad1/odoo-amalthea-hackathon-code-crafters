import smtplib
import secrets
import string
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware


from . import crud, schemas, database
from .database import SessionLocal, engine

# Create the database tables
database.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Simple Auth Backend",
    description="A simple backend with login notifications and password reset.",
    version="1.0.0"
)

# --- Add CORS Middleware ---
# This allows your frontend (e.g., from Netlify) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend's actual URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- SECURITY & AUTHENTICATION HELPERS ---

# Load settings from environment variables (from .env file)
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    SECRET_KEY: str = "your-default-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env"
settings = Settings()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") # Changed to match frontend call

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- EMAIL SENDING FUNCTION ---

def send_email(to_email: str, subject: str, body: str):
    """Sends an email using the SMTP settings from the .env file."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"LedgerCore <{settings.SMTP_USER}>"
    msg['To'] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- API ENDPOINTS ---

# Dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/signup", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # --- Send Login Notification Email TO THE USER ---
    subject = "Security Alert: New Login to Your LedgerCore Account"
    body = f"Hello {user.name},\n\nWe detected a new login to your account at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nIf this was not you, please reset your password immediately."
    send_email(to_email=user.email, subject=subject, body=body)

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/forgot-password", response_model=schemas.Msg)
def forgot_password_endpoint(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        # For security, we don't reveal if an email exists.
        return {"msg": "If an account with that email exists, a password reset link has been sent."}

    # --- Generate a new random password ---
    new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
    hashed_password = get_password_hash(new_password)
    crud.update_user_password(db, user=user, hashed_password=hashed_password)
    
    # --- Email the new password to the user ---
    subject = "Your Password Has Been Reset"
    body = f"Hello {user.name},\n\nYour password for LedgerCore has been reset.\n\nYour new temporary password is: {new_password}\n\nPlease log in and change it immediately from your profile settings."
    send_email(to_email=user.email, subject=subject, body=body)

    return {"msg": "If an account with that email exists, a password reset link has been sent."}

# You will need to implement this endpoint for the frontend's dashboard to work
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(crud.get_current_user)):
    return current_user
