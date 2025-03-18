from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.auth.models import User
from app.auth.schemas import UserCreate, UserUpdate
from app.auth.dependencies import create_access_token
from app.utils.errors import NotFoundError, ValidationError, ConflictError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        return User.objects(username=username).first()

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        return User.objects(email=email).first()

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        user = await AuthService.get_user_by_username(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        # Check if user with same username or email already exists
        if await AuthService.get_user_by_username(user_data.username):
            raise ConflictError(
                message="Username already exists",
                details={"username": user_data.username}
            )

        if await AuthService.get_user_by_email(user_data.email):
            raise ConflictError(
                message="Email already exists",
                details={"email": user_data.email}
            )

        # Create new user
        hashed_password = AuthService.get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password

        user = User(**user_dict)
        user.save()

        return user

    @staticmethod
    async def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
        return create_access_token(
            data={"sub": str(user.id)},
            expires_delta=expires_delta
        )

auth_service = AuthService()
