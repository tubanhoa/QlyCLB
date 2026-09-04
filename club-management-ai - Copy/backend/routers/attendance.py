"""
Router: Attendance - Quản lý điểm danh
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Attendance, Activity, Member, User
from schemas import AttendanceCreate, AttendanceUpdate, AttendanceBulkCreate
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("")
def get_attendance(
    activity_id: Optional[int] = Query(None),
    member_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách điểm danh"""
    query = db.query(Attendance)

    if activity_id:
        query = query.filter(Attendance.activity_id == activity_id)

    if member_id:
        query = query.filter(Attendance.member_id == member_id)

    records = query.all()

    result = []
    for r in records:
        member = db.query(Member).filter(Member.id == r.member_id).first()
        activity = db.query(Activity).filter(Activity.id == r.activity_id).first()

        result.append({
            "id": r.id,
            "activity_id": r.activity_id,
            "activity_name": activity.name if activity else None,
            "member_id": r.member_id,
            "member_name": member.name if member else None,
            "status": r.status
        })

    return result


@router.post("")
def create_attendance(
    data: AttendanceCreate,
    current_user: User = Depends(require_role(["chu_nhiem", "truong_ban"])),
    db: Session = Depends(get_db)
):
    """Tạo bản ghi điểm danh"""
    # Kiểm tra hoạt động tồn tại
    activity = db.query(Activity).filter(Activity.id == data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động")

    # Kiểm tra thành viên tồn tại
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên")

    # Kiểm tra đã điểm danh chưa
    existing = db.query(Attendance).filter(
        Attendance.activity_id == data.activity_id,
        Attendance.member_id == data.member_id
    ).first()

    if existing:
        # Cập nhật nếu đã có
        existing.status = data.status
        db.commit()
        return {"message": "Cập nhật điểm danh thành công", "id": existing.id}

    new_record = Attendance(**data.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {"message": "Điểm danh thành công", "id": new_record.id}


@router.post("/bulk")
def bulk_attendance(
    data: AttendanceBulkCreate,
    current_user: User = Depends(require_role(["chu_nhiem", "truong_ban"])),
    db: Session = Depends(get_db)
):
    """Điểm danh hàng loạt cho một hoạt động"""
    activity = db.query(Activity).filter(Activity.id == data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động")

    for record in data.records:
        existing = db.query(Attendance).filter(
            Attendance.activity_id == data.activity_id,
            Attendance.member_id == record.member_id
        ).first()

        if existing:
            existing.status = record.status
        else:
            new_record = Attendance(
                activity_id=data.activity_id,
                member_id=record.member_id,
                status=record.status
            )
            db.add(new_record)

    db.commit()
    return {"message": "Điểm danh hàng loạt thành công"}


@router.put("/{attendance_id}")
def update_attendance(
    attendance_id: int,
    data: AttendanceUpdate,
    current_user: User = Depends(require_role(["chu_nhiem", "truong_ban"])),
    db: Session = Depends(get_db)
):
    """Cập nhật trạng thái điểm danh"""
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi điểm danh")

    record.status = data.status
    db.commit()

    return {"message": "Cập nhật điểm danh thành công"}


@router.get("/stats/{activity_id}")
def get_attendance_stats(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thống kê điểm danh cho một hoạt động"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động")

    total = db.query(Attendance).filter(Attendance.activity_id == activity_id).count()
    present = db.query(Attendance).filter(
        Attendance.activity_id == activity_id,
        Attendance.status == "present"
    ).count()
    absent = db.query(Attendance).filter(
        Attendance.activity_id == activity_id,
        Attendance.status == "absent"
    ).count()
    excused = db.query(Attendance).filter(
        Attendance.activity_id == activity_id,
        Attendance.status == "excused"
    ).count()

    rate = round((present / total * 100), 1) if total > 0 else 0

    return {
        "activity_id": activity_id,
        "activity_name": activity.name,
        "total": total,
        "present": present,
        "absent": absent,
        "excused": excused,
        "attendance_rate": rate
    }
