from pydantic import BaseModel
from typing import Optional, List

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str
    full_name: str
    email: Optional[str] = None
    is_authenticated: bool
    access_token: str
    token_type: str = "bearer"