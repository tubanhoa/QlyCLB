"""
Router: Tasks - Quản lý nhiệm vụ
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Task, Activity, Member, User
from schemas import TaskCreate, TaskUpdate
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("")
def get_tasks(
    activity_id: Optional[int] = Query(None),
    assigned_to: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("deadline"),
    order: Optional[str] = Query("asc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách nhiệm vụ (hỗ trợ tìm kiếm, lọc và sắp xếp)"""
    query = db.query(Task)

    # Thành viên chỉ xem nhiệm vụ được giao
    if current_user.role == "thanh_vien" and current_user.member_id:
        query = query.filter(Task.assigned_to == current_user.member_id)

    # Trưởng ban xem nhiệm vụ ban mình
    if current_user.role == "truong_ban" and current_user.member_id:
        current_member = db.query(Member).filter(Member.id == current_user.member_id).first()
        if current_member and current_member.department_id:
            dept_members = db.query(Member.id).filter(
                Member.department_id == current_member.department_id
            ).all()
            member_ids = [m.id for m in dept_members]
            query = query.filter(
                (Task.assigned_to.in_(member_ids)) |
                (Task.assigned_by == current_user.member_id)
            )

    if activity_id:
        query = query.filter(Task.activity_id == activity_id)

    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if search:
        query = query.filter(
            (Task.name.contains(search)) |
            (Task.description.contains(search))
        )

    # Sắp xếp
    sort_column = Task.deadline
    if sort_by == "priority":
        sort_column = Task.priority
    elif sort_by == "progress":
        sort_column = Task.progress
    elif sort_by == "name":
        sort_column = Task.name
    elif sort_by == "id":
        sort_column = Task.id

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    tasks = query.all()

    result = []
    for t in tasks:
        activity_name = None
        if t.activity_id:
            activity = db.query(Activity).filter(Activity.id == t.activity_id).first()
            if activity:
                activity_name = activity.name

        assignee_name = None
        if t.assigned_to:
            assignee = db.query(Member).filter(Member.id == t.assigned_to).first()
            if assignee:
                assignee_name = assignee.name

        assigner_name = None
        if t.assigned_by:
            assigner = db.query(Member).filter(Member.id == t.assigned_by).first()
            if assigner:
                assigner_name = assigner.name

        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "activity_id": t.activity_id,
            "activity_name": activity_name,
            "assigned_to": t.assigned_to,
            "assignee_name": assignee_name,
            "assigned_by": t.assigned_by,
            "assigner_name": assigner_name,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "status": t.status,
            "progress": t.progress,
            "priority": t.priority
        })

    return result


@router.post("")
def create_task(
    task: TaskCreate,
    current_user: User = Depends(require_role(["chu_nhiem", "truong_ban"])),
    db: Session = Depends(get_db)
):
    """Tạo nhiệm vụ (Chủ nhiệm hoặc Trưởng ban)"""
    # Gán người giao = member_id của user hiện tại
    task_data = task.model_dump()
    if current_user.member_id:
        task_data["assigned_by"] = current_user.member_id

    new_task = Task(**task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "Tạo nhiệm vụ thành công", "id": new_task.id}


@router.put("/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật nhiệm vụ"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhiệm vụ")

    # Thành viên chỉ được cập nhật tiến độ và trạng thái
    if current_user.role == "thanh_vien":
        if task.assigned_to != current_user.member_id:
            raise HTTPException(status_code=403, detail="Không có quyền cập nhật nhiệm vụ này")
        allowed_fields = ["status", "progress"]
        update_data = task_data.model_dump(exclude_unset=True)
        for key in list(update_data.keys()):
            if key not in allowed_fields:
                del update_data[key]
    else:
        update_data = task_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    return {"message": "Cập nhật nhiệm vụ thành công"}


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(require_role(["chu_nhiem", "truong_ban"])),
    db: Session = Depends(get_db)
):
    """Xóa nhiệm vụ"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhiệm vụ")

    db.delete(task)
    db.commit()

    return {"message": "Xóa nhiệm vụ thành công"}
