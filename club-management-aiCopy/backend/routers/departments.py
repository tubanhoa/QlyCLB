"""
Router: Departments - Quản lý ban chuyên môn
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Department, Member, User
from schemas import DepartmentCreate, DepartmentUpdate
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get("")
def get_departments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách ban chuyên môn"""
    departments = db.query(Department).all()

    result = []
    for dept in departments:
        leader_name = None
        if dept.leader_id:
            leader = db.query(Member).filter(Member.id == dept.leader_id).first()
            if leader:
                leader_name = leader.name

        member_count = db.query(Member).filter(Member.department_id == dept.id).count()

        result.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "leader_id": dept.leader_id,
            "leader_name": leader_name,
            "member_count": member_count
        })

    return result


@router.post("")
def create_department(
    dept: DepartmentCreate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Thêm ban mới (Chỉ chủ nhiệm)"""
    existing = db.query(Department).filter(Department.name == dept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tên ban đã tồn tại")

    new_dept = Department(**dept.model_dump())
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)

    return {"message": "Thêm ban thành công", "id": new_dept.id}


@router.get("/{dept_id}")
def get_department(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xem chi tiết ban"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Không tìm thấy ban")

    leader_name = None
    if dept.leader_id:
        leader = db.query(Member).filter(Member.id == dept.leader_id).first()
        if leader:
            leader_name = leader.name

    members = db.query(Member).filter(Member.department_id == dept.id).all()
    member_list = [{"id": m.id, "name": m.name, "email": m.email} for m in members]

    return {
        "id": dept.id,
        "name": dept.name,
        "description": dept.description,
        "leader_id": dept.leader_id,
        "leader_name": leader_name,
        "members": member_list,
        "member_count": len(member_list)
    }


@router.put("/{dept_id}")
def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Sửa ban (Chỉ chủ nhiệm)"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Không tìm thấy ban")

    update_data = dept_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dept, key, value)

    db.commit()
    return {"message": "Cập nhật ban thành công"}


@router.delete("/{dept_id}")
def delete_department(
    dept_id: int,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Xóa ban (Chỉ chủ nhiệm)"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Không tìm thấy ban")

    # Xóa liên kết thành viên
    db.query(Member).filter(Member.department_id == dept_id).update(
        {Member.department_id: None}
    )

    db.delete(dept)
    db.commit()

    return {"message": "Xóa ban thành công"}
