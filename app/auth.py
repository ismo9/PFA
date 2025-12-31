from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Mock user database (in production, use real DB with hashed passwords)
# For demo purposes, storing plain passwords to avoid bcrypt compatibility issues
MOCK_USERS = {
    "admin@erp.com": {
        "username": "admin@erp.com",
        "full_name": "Admin User",
        "email": "admin@erp.com",
        "hashed_password": "admin123",  # plain for demo (use hashing in production!)
        "role": "admin",
        "disabled": False,
    },
    "viewer@erp.com": {
        "username": "viewer@erp.com",
        "full_name": "Viewer User",
        "email": "viewer@erp.com",
        "hashed_password": "viewer123",  # plain for demo
        "role": "viewer",
        "disabled": False,
    },
    "manager@erp.com": {
        "username": "manager@erp.com",
        "full_name": "Manager User",
        "email": "manager@erp.com",
        "hashed_password": "manager123",  # plain for demo
        "role": "manager",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    # For demo, use plain comparison (in production, use pwd_context.verify)
    return plain_password == hashed_password


def get_password_hash(password):
    # For demo, return plain password (in production, use pwd_context.hash)
    return password


def get_user(username: str):
    if username in MOCK_USERS:
        user_dict = MOCK_USERS[username]
        return UserInDB(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Optional: role-based dependency
def require_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
