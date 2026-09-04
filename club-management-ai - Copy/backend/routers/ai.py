"""
Router: AI - Các chức năng AI
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import AIRequest, Activity, Member, Task, User
from schemas import AINotificationRequest, AISummarizeRequest, AIAssignTaskRequest, AIResponse, ChatRequest
from auth import get_current_user, require_role
from services.ai_service import generate_notification, summarize_activity, suggest_task_assignment
from services.chatbot_service import chat_with_assistant

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/notification", response_model=AIResponse)
async def ai_generate_notification(
    data: AINotificationRequest,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """AI sinh thông báo hoạt động"""
    result = await generate_notification(
        activity_name=data.activity_name,
        time=data.time or "",
        location=data.location or "",
        content=data.content or "",
        target_audience=data.target_audience or ""
    )

    # Lưu lịch sử AI
    ai_request = AIRequest(
        type="notification",
        input_data=json.dumps(data.model_dump(), ensure_ascii=False),
        output_data=result
    )
    db.add(ai_request)
    db.commit()

    return AIResponse(result=result, type="notification")


@router.post("/summarize", response_model=AIResponse)
async def ai_summarize_activity(
    data: AISummarizeRequest,
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """AI tóm tắt hoạt động"""
    result = await summarize_activity(
        activity_name=data.activity_name,
        description=data.description or "",
        notes=data.notes or "",
        result=data.result or "",
        feedback=data.feedback or ""
    )

    # Lưu lịch sử AI
    ai_request = AIRequest(
        type="summarize",
        input_data=json.dumps(data.model_dump(), ensure_ascii=False),
        output_data=result
    )
    db.add(ai_request)
    db.commit()

    return AIResponse(result=result, type="summarize")


@router.post("/assign-task", response_model=AIResponse)
async def ai_assign_task(
    data: AIAssignTaskRequest,
    current_user: User = Depends(require_role(["chu_nhiem", "truong_ban"])),
    db: Session = Depends(get_db)
):
    """AI gợi ý phân công nhiệm vụ"""
    # Lấy thông tin hoạt động
    activity_info = data.activity_info or ""
    if data.activity_id:
        activity = db.query(Activity).filter(Activity.id == data.activity_id).first()
        if activity:
            activity_info = f"{activity.name} - {activity.description or 'Không có mô tả'}"

    # Lấy danh sách thành viên với kỹ năng
    members = db.query(Member).filter(Member.status == "active").all()
    member_skills = ""
    availability = ""
    for m in members:
        dept_name = ""
        if m.department:
            dept_name = m.department.name
        member_skills += f"- {m.name} (Ban: {dept_name}, Kỹ năng: {m.skills or 'Chưa cập nhật'})\n"
        availability += f"- {m.name}: {m.availability or 'Chưa cập nhật'}\n"

    # Danh sách nhiệm vụ
    task_list = data.task_list or ""
    if not task_list and data.activity_id:
        tasks = db.query(Task).filter(Task.activity_id == data.activity_id).all()
        for t in tasks:
            task_list += f"- {t.name} (Ưu tiên: {t.priority})\n"

    result = await suggest_task_assignment(
        activity_info=activity_info,
        member_skills=member_skills,
        availability=availability,
        tasks=task_list
    )

    # Lưu lịch sử AI
    ai_request = AIRequest(
        type="assign_task",
        input_data=json.dumps({
            "activity_info": activity_info,
            "member_count": len(members),
            "task_list": task_list
        }, ensure_ascii=False),
        output_data=result
    )
    db.add(ai_request)
    db.commit()

    return AIResponse(result=result, type="assign_task")


@router.get("/history")
def get_ai_history(
    current_user: User = Depends(require_role(["chu_nhiem"])),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử yêu cầu AI"""
    requests = db.query(AIRequest).order_by(AIRequest.created_at.desc()).limit(50).all()

    return [
        {
            "id": r.id,
            "type": r.type,
            "input_data": r.input_data,
            "output_data": r.output_data,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in requests
    ]


@router.post("/chat")
async def ai_chat(
    data: ChatRequest,
    db: Session = Depends(get_db)
):
    """UniClub Assistant - Chatbot cho sinh viên (public, không cần đăng nhập)"""
    result = await chat_with_assistant(message=data.message, db=db)

    # Lưu lịch sử AI
    ai_request = AIRequest(
        type="chatbot",
        input_data=json.dumps({"message": data.message}, ensure_ascii=False),
        output_data=json.dumps(result, ensure_ascii=False)
    )
    db.add(ai_request)
    db.commit()

    return result
