"""
Router: Members - Quản lý thành viên
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Member, Department, User
from schemas import MemberCreate, MemberUpdate, MemberResponse
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/members", tags=["Members"])


@router.get("")
def get_members(
    department_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    order: Optional[str] = Query("asc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách thành viên (hỗ trợ tìm kiếm, lọc và sắp xếp)"""
    query = db.query(Member)

    # Trưởng ban chỉ xem thành viên ban mình
    if current_user.role == "truong_ban" and current_user.member_id:
        member = db.query(Member).filter(Member.id == current_user.member_id).first()
        if member and member.department_id:
            query = query.filter(Member.department_id == member.department_id)

    # Thành viên chỉ xem thông tin cá nhân
    if current_user.role == "thanh_vien" and current_user.member_id:
        query = query.filter(Member.id == current_user.member_id)

    # Lọc theo ban
    if department_id:
        query = query.filter(Member.department_id == department_id)

    # Tìm kiếm
    if search:
        query = query.filter(
            (Member.name.contains(search)) |
            (Member.email.contains(search)) |
            (Member.phone.contains(search))
        )

    # Lọc theo trạng thái
    if status:
        query = query.filter(Member.status == status)

    # Sắp xếp
    sort_column = Member.id
    if sort_by == "name":
        sort_column = Member.name
    elif sort_by == "join_date":
        sort_column = Member.join_date

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    members = query.all()

    result = []
    for m in members:
        dept_name = None
        if m.department_id:
            dept = db.query(Department).filter(Department.id == m.department_id).first()
            if dept:
                dept_name = dept.name

        result.append({
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone,
            "department_id": m.department_id,
            "department_name": dept_name,
            "skills": m.skills,
            "availability": m.availability,
            "join_date": m.join_date.isoformat() if m.join_date else None,
            "status": m.status
        })

    return result


@router.post("")
def create_member(
    member: MemberCreate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Thêm thành viên mới (Chỉ chủ nhiệm)"""
    # Kiểm tra email trùng
    existing = db.query(Member).filter(Member.email == member.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    new_member = Member(**member.model_dump())
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {"message": "Thêm thành viên thành công", "id": new_member.id}


@router.get("/{member_id}")
def get_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xem chi tiết thành viên"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

    # Thành viên chỉ xem thông tin mình
    if current_user.role == "thanh_vien" and current_user.member_id != member_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem thông tin này")

    dept_name = None
    if member.department_id:
        dept = db.query(Department).filter(Department.id == member.department_id).first()
        if dept:
            dept_name = dept.name

    return {
        "id": member.id,
        "name": member.name,
        "email": member.email,
        "phone": member.phone,
        "department_id": member.department_id,
        "department_name": dept_name,
        "skills": member.skills,
        "availability": member.availability,
        "join_date": member.join_date.isoformat() if member.join_date else None,
        "status": member.status
    }


@router.put("/{member_id}")
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sửa thông tin thành viên"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

    # Thành viên chỉ sửa thông tin mình (giới hạn trường)
    if current_user.role == "thanh_vien":
        if current_user.member_id != member_id:
            raise HTTPException(status_code=403, detail="Không có quyền sửa thông tin này")
        # Chỉ cho phép sửa một số trường
        allowed_fields = ["phone", "skills", "availability"]
        update_data = member_data.model_dump(exclude_unset=True)
        for key in list(update_data.keys()):
            if key not in allowed_fields:
                del update_data[key]
    elif current_user.role == "truong_ban":
        # Trưởng ban sửa thành viên ban mình
        current_member = db.query(Member).filter(Member.id == current_user.member_id).first()
        if current_member and member.department_id != current_member.department_id:
            raise HTTPException(status_code=403, detail="Không có quyền sửa thành viên ban khác")
        update_data = member_data.model_dump(exclude_unset=True)
    else:
        update_data = member_data.model_dump(exclude_unset=True)

    # Kiểm tra email trùng nếu có thay đổi email
    if "email" in update_data and update_data["email"] and update_data["email"] != member.email:
        duplicate = db.query(Member).filter(Member.email == update_data["email"], Member.id != member_id).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi thành viên khác")

    for key, value in update_data.items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)

    return {"message": "Cập nhật thành viên thành công"}


@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Xóa thành viên (Chỉ chủ nhiệm)"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

    db.delete(member)
    db.commit()

    return {"message": "Xóa thành viên thành công"}
