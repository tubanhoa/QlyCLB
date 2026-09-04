"""
Authentication - JWT Token + Password Hashing
"""
import os
import hashlib
import json
import base64
import hmac
import time
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User

# Secret key cho JWT (đơn giản cho đồ án)
SECRET_KEY = os.getenv("SECRET_KEY", "club-management-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password bằng SHA-256 (đơn giản cho đồ án)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh password"""
    return hash_password(plain_password) == hashed_password


def create_token(data: dict) -> str:
    """Tạo JWT token đơn giản"""
    # Header
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": ALGORITHM, "typ": "JWT"}).encode()
    ).decode().rstrip("=")

    # Payload
    payload_data = data.copy()
    payload_data["exp"] = time.time() + (ACCESS_TOKEN_EXPIRE_HOURS * 3600)
    payload = base64.urlsafe_b64encode(
        json.dumps(payload_data).encode()
    ).decode().rstrip("=")

    # Signature
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header}.{payload}".encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{header}.{payload}.{signature}"


def decode_token(token: str) -> dict:
    """Giải mã JWT token"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")

        header, payload, signature = parts

        # Verify signature
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{header}.{payload}".encode(),
            hashlib.sha256
        ).hexdigest()

        if signature != expected_sig:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")

        # Decode payload
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        payload_data = json.loads(base64.urlsafe_b64decode(payload))

        # Check expiration
        if payload_data.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token đã hết hạn")

        return payload_data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: Lấy user hiện tại từ token"""
    token = credentials.credentials
    payload = decode_token(token)

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")

    return user


def require_role(allowed_roles: list):
    """Dependency: Kiểm tra quyền truy cập theo vai trò"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền thực hiện thao tác này"
            )
        return current_user
    return role_checker
