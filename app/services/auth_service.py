from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.database.connection import get_db
from app.models.user import User
from app.models.transaction import UserTotal

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-here")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_expire_minutes = 60  # 1 hour
        self.security = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Şifre doğrulama"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Şifre hashleme"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """JWT token oluşturma"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> str:
        """JWT token doğrulama"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return user_id
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Email ile kullanıcı bulma"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """ID ile kullanıcı bulma"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_data) -> User:
        """Yeni kullanıcı oluşturma"""
        hashed_password = self.get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            phone=user_data.phone,
            password_hash=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create user totals record
        user_total = UserTotal(user_id=new_user.id)
        db.add(user_total)
        await db.commit()
        
        return new_user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Kullanıcı kimlik doğrulama"""
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user

    async def get_current_user(
        self, 
        token = Depends(HTTPBearer()),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Mevcut kullanıcıyı token'dan alma"""
        user_id = self.verify_token(token.credentials)
        user = await self.get_user_by_id(db, user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user 