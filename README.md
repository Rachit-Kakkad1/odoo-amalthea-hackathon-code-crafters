# Expense Management Backend

Backend API for managing expenses with approval workflows, built with FastAPI.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set env vars (e.g., in `.env`):
   - `DATABASE_URL=postgresql+psycopg://user:pass@localhost/db`
   - `SECRET_KEY=your-secret`
   - `EXCHANGE_API_KEY=your-exchangerate-api-key` (if required for premium features)
3. Run migrations: `alembic upgrade head`
4. Start server: `uvicorn app.main:app --reload`

## Features
- User signup/login with auto-company creation.
- Expense submission with OCR and currency conversion.
- Flexible approval rules (sequential, conditional, hybrid).
- Role-based access.

API Docs: `/docs`