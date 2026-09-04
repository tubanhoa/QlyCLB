"""
Router: Authentication - Đăng nhập
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, LoginResponse
from auth import verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập và trả về JWT token"""
    # Tìm user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không đúng")

    # Kiểm tra password
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không đúng")

    # Tạo token
    token = create_token({
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "member_id": user.member_id
    })

    return LoginResponse(
        token=token,
        role=user.role,
        user_id=user.id,
        member_id=user.member_id,
        username=user.username
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin user hiện tại"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "member_id": current_user.member_id
    }
