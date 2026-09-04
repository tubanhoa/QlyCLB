"""
Pydantic Schemas - Validation cho request/response
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ==================== AUTH ====================
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    role: str
    user_id: int
    member_id: Optional[int] = None
    username: str

class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    member_id: Optional[int] = None


# ==================== MEMBER ====================
class MemberCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[int] = None
    skills: Optional[str] = None
    availability: Optional[str] = None
    status: Optional[str] = "active"

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    skills: Optional[str] = None
    availability: Optional[str] = None
    status: Optional[str] = None

class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    skills: Optional[str] = None
    availability: Optional[str] = None
    join_date: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True


# ==================== DEPARTMENT ====================
class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    leader_id: Optional[int] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    leader_id: Optional[int] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    leader_id: Optional[int] = None
    leader_name: Optional[str] = None
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ==================== ACTIVITY ====================
class ActivityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    manager_id: Optional[int] = None
    status: Optional[str] = "upcoming"
    notes: Optional[str] = None
    result: Optional[str] = None

class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    result: Optional[str] = None

class ActivityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    manager_id: Optional[int] = None
    manager_name: Optional[str] = None
    status: str
    notes: Optional[str] = None
    result: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== ATTENDANCE ====================
class AttendanceCreate(BaseModel):
    activity_id: int
    member_id: int
    status: str = "absent"  # present, absent, excused

class AttendanceUpdate(BaseModel):
    status: str  # present, absent, excused

class AttendanceBulkCreate(BaseModel):
    activity_id: int
    records: List[AttendanceCreate]

class AttendanceResponse(BaseModel):
    id: int
    activity_id: int
    member_id: int
    member_name: Optional[str] = None
    activity_name: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ==================== TASK ====================
class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    activity_id: Optional[int] = None
    assigned_to: Optional[int] = None
    assigned_by: Optional[int] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = "not_started"
    progress: Optional[int] = 0
    priority: Optional[str] = "medium"

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    activity_id: Optional[int] = None
    assigned_to: Optional[int] = None
    assigned_by: Optional[int] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    priority: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    activity_id: Optional[int] = None
    activity_name: Optional[str] = None
    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None
    assigned_by: Optional[int] = None
    assigner_name: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str
    progress: int
    priority: str

    class Config:
        from_attributes = True


# ==================== NOTIFICATION ====================
class NotificationCreate(BaseModel):
    title: str
    content: str

class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    created_by: Optional[int] = None
    creator_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== AI ====================
class AINotificationRequest(BaseModel):
    activity_name: str
    time: Optional[str] = None
    location: Optional[str] = None
    content: Optional[str] = None
    target_audience: Optional[str] = None

class AISummarizeRequest(BaseModel):
    activity_name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    result: Optional[str] = None
    feedback: Optional[str] = None

class AIAssignTaskRequest(BaseModel):
    activity_id: Optional[int] = None
    activity_info: Optional[str] = None
    task_list: Optional[str] = None

class AIResponse(BaseModel):
    result: str
    type: str


# ==================== CHATBOT ====================
class ChatRequest(BaseModel):
    message: str

class SuggestedClub(BaseModel):
    maDinhDanh: str
    tenClb: str
    lyDoGoiY: str

class ChatResponse(BaseModel):
    answer: str
    suggestedClubs: List[SuggestedClub] = []
    followUpQuestions: List[str] = []
