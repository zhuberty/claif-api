from functools import wraps
from fastapi import HTTPException


def value_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        # You can add more exception types here if needed
    return wrapper