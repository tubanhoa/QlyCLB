"""
Router: Activities - Quản lý hoạt động
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Activity, Member, User
from schemas import ActivityCreate, ActivityUpdate
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/activities", tags=["Activities"])


@router.get("")
def get_activities(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách hoạt động"""
    query = db.query(Activity)

    if status:
        query = query.filter(Activity.status == status)

    if search:
        query = query.filter(
            (Activity.name.contains(search)) |
            (Activity.description.contains(search))
        )

    activities = query.order_by(Activity.date.desc()).all()

    result = []
    for a in activities:
        manager_name = None
        if a.manager_id:
            manager = db.query(Member).filter(Member.id == a.manager_id).first()
            if manager:
                manager_name = manager.name

        result.append({
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "date": a.date.isoformat() if a.date else None,
            "location": a.location,
            "manager_id": a.manager_id,
            "manager_name": manager_name,
            "status": a.status,
            "notes": a.notes,
            "result": a.result
        })

    return result


@router.post("")
def create_activity(
    activity: ActivityCreate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Thêm hoạt động (Chỉ chủ nhiệm)"""
    new_activity = Activity(**activity.model_dump())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return {"message": "Thêm hoạt động thành công", "id": new_activity.id}


@router.get("/{activity_id}")
def get_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xem chi tiết hoạt động"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động")

    manager_name = None
    if activity.manager_id:
        manager = db.query(Member).filter(Member.id == activity.manager_id).first()
        if manager:
            manager_name = manager.name

    return {
        "id": activity.id,
        "name": activity.name,
        "description": activity.description,
        "date": activity.date.isoformat() if activity.date else None,
        "location": activity.location,
        "manager_id": activity.manager_id,
        "manager_name": manager_name,
        "status": activity.status,
        "notes": activity.notes,
        "result": activity.result
    }


@router.put("/{activity_id}")
def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Sửa hoạt động (Chỉ chủ nhiệm)"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động")

    update_data = activity_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(activity, key, value)

    db.commit()
    return {"message": "Cập nhật hoạt động thành công"}


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Xóa hoạt động (Chỉ chủ nhiệm)"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động")

    db.delete(activity)
    db.commit()

    return {"message": "Xóa hoạt động thành công"}
