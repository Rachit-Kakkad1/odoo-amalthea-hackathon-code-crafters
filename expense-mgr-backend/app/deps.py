from fastapi import Depends, HTTPException, status
from . import models
from .auth import get_current_user

# This is an example of a higher-level dependency.
# It depends on get_current_user to do its job.
# This is a clean pattern with no circular imports.
async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user
