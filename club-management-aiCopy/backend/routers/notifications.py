"""
Router: Notifications - Quản lý thông báo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Notification, User
from schemas import NotificationCreate
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
def get_notifications(
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách thông báo (hỗ trợ tìm kiếm và sắp xếp)"""
    query = db.query(Notification)

    if search:
        query = query.filter(
            (Notification.title.contains(search)) |
            (Notification.content.contains(search))
        )

    sort_col = Notification.created_at
    if sort_by == "title":
        sort_col = Notification.title

    if order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    notifications = query.all()

    result = []
    for n in notifications:
        creator_name = None
        if n.created_by:
            creator = db.query(User).filter(User.id == n.created_by).first()
            if creator:
                creator_name = creator.username

        result.append({
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "created_by": n.created_by,
            "creator_name": creator_name,
            "created_at": n.created_at.isoformat() if n.created_at else None
        })

    return result


@router.post("")
def create_notification(
    data: NotificationCreate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Tạo thông báo (Chỉ chủ nhiệm)"""
    new_notification = Notification(
        title=data.title,
        content=data.content,
        created_by=current_user.id
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return {"message": "Tạo thông báo thành công", "id": new_notification.id}


@router.put("/{notification_id}")
def update_notification(
    notification_id: int,
    data: NotificationCreate,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Sửa thông báo"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")

    notification.title = data.title
    notification.content = data.content
    db.commit()

    return {"message": "Cập nhật thông báo thành công"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Xóa thông báo (Chỉ chủ nhiệm)"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")

    db.delete(notification)
    db.commit()

    return {"message": "Xóa thông báo thành công"}
