from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from uuid import UUID, uuid4
from app.core.config import settings
from typing import Optional, Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt import PyJWTError
from app.database import get_db, SessionLocal
from app.models.models import User
from app.schema import RegisterUserRequest, TokenData, UserResponse, PasswordChange
from app.exceptions import AuthenticationError, UserNotFoundError, InvalidPasswordError, PasswordMismatchError
import logging

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]

def verify_password(plain_password, hashed_password):
    """verify plain password aganist the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_hashed_password(password):
    """Generate bcrypt hash from the plain password"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        user_id = payload.get('id')
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("Token payload missing 'id' or 'id' is not a string")
        return TokenData(user_id=user_id)
    except PyJWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise 

async def register_user(db: db_dependency, register_user: RegisterUserRequest) -> None:
    try:
        create_user_request = User(
            id = uuid4(),
            user_name = register_user.username,
            first_name = register_user.first_name,
            last_name = register_user.last_name,
            email = register_user.email,
            phone_number = register_user.phone_number,
            hashed_password = register_user.password    
        )
        db.add(create_user_request)
        db.commit()
        db.refresh(create_user_request)
    except Exception as e:
        logging.error(f"Failed to register user: {register_user.email}. Error: {str(e)}")
        raise AuthenticationError()
    


async def get_current_user(request: Request,db: Session = Depends(get_db)):
    """Get current user from cookie"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token = request.cookies.get("access_token")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]) #type: ignore
        email: str = payload.get("sub") #type: ignore
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,  detail="Token has expired")
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# async def get_current_user(request: Request, db=db_dependency):
#     """Get current user from the cookie"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail= "Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"}
#     )
#     token = request.cookies.get("access_token")
#     print(f"[DEBUG] access_token from cookie: {token}")
#     if token is None:
#         print("[DEBUG] No access_token cookie found.")
#         raise credentials_exception

#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         print(f"[DEBUG] Decoded JWT payload: {payload}")
#         email = payload.get("sub")
#         if not isinstance(email, str) or not email:
#             print("[DEBUG] No valid 'sub' in JWT payload.")
#             raise credentials_exception
#     except JWTError as e:
#         print(f"[DEBUG] JWTError: {e}")
#         raise credentials_exception
#     user = db.query(User).filter(User.email == email).first()  # type: ignore
#     if user is None:
#         print(f"[DEBUG] No user found in DB for email: {email}")
#         raise credentials_exception
#     print(f"[DEBUG] Authenticated user: {user.email}")
#     return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user"""
    if not current_user.is_active:  #type: ignore
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access toekn"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_user_by_id(db: Session, user_id: UUID) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.warning(f"User not found with ID: {user_id}")
        raise UserNotFoundError()
    logging.info(f"Successfully retrieved user with ID: {user_id}")
    return user

def change_password(db: Session, user_id: UUID, password_change: PasswordChange) -> None:
    try:
        user = get_user_by_id(db=db, user_id=user_id)

        # verify current password
        if not verify_password(password_change.current_password, user.hashed_password):
            logging.warning(f"Invalid current password provided for user ID: {user_id}")
            raise InvalidPasswordError()
        
        # Verify new password match
        if password_change.new_password != password_change.new_password_confirm:
            logging.warning(f"Password mismatch during attempt for user ID: {user_id}")
            raise PasswordMismatchError()
        
        # Update password
        user.hashed_password = get_hashed_password(password_change.new_password)
        db.commit()
        logging.info(f"Successfully change password for user ID: {user_id}")
    except Exception as e:
        logging.error(f"Error during password change for user ID: {user_id}. Error: {str(e)}")
        raise