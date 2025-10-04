import uvicorn
import sys
import os

# This adds the project root to Python's path, fixing import issues.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    # This command starts the Uvicorn server, pointing to the app instance in app/main.py
    # It will use 'watchfiles' automatically because it's in requirements.txt.
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
    )


#### 2. Environment Variables (`.env`)
This file holds all your secret keys. **Do not commit this file to GitHub.**

.env (Template):.env
# Database Connection
DATABASE_URL=postgresql+asyncpg://admin:secret@localhost:5432/expenses

# Authentication
SECRET_KEY=a_very_secret_key_change_me_please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RESET_TOKEN_EXPIRE_MINUTES=30

# Email Settings (Example for Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-google-app-password

# SMS Settings (Placeholder)
SMS_API_URL=https://api.example.com/sms
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=EXPENSEMGR

# Application Settings
APP_NAME="Expense Management System"
DEBUG=True
LOG_LEVEL=INFO


#### 3. Project Dependencies (`requirements.txt`)
This file lists all the necessary Python packages.

Project Dependencies:requirements.txt
# Core Framework
fastapi
uvicorn[standard]
watchfiles

# Database
sqlalchemy[asyncio]
psycopg[binary,pool]
alembic
asyncpg

# Pydantic & Config
pydantic[email]
pydantic-settings

# Security
passlib[bcrypt]
python-jose[cryptography]

# Utilities
python-multipart
requests
structlog
