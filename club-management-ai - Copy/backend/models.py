"""
SQLAlchemy ORM Models - 8 bảng chính
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """Bảng users - Tài khoản đăng nhập"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hashed password
    role = Column(String(20), nullable=False)  # chu_nhiem, truong_ban, thanh_vien
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    # Relationships
    member = relationship("Member", back_populates="user")
    notifications = relationship("Notification", back_populates="creator")


class Member(Base):
    """Bảng members - Thông tin thành viên"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    skills = Column(Text, nullable=True)  # Lưu dạng chuỗi, phân cách bằng dấu phẩy
    availability = Column(Text, nullable=True)  # Lịch rảnh
    join_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="active")  # active, inactive

    # Relationships
    user = relationship("User", back_populates="member", uselist=False)
    department = relationship("Department", back_populates="members", foreign_keys=[department_id])
    attendances = relationship("Attendance", back_populates="member")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")


class Department(Base):
    """Bảng departments - Ban chuyên môn"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    leader_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    # Relationships
    members = relationship("Member", back_populates="department", foreign_keys="Member.department_id")
    leader = relationship("Member", foreign_keys=[leader_id])


class Activity(Base):
    """Bảng activities - Hoạt động CLB"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    location = Column(String(200), nullable=True)
    manager_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    status = Column(String(30), default="upcoming")  # upcoming, ongoing, completed, cancelled
    notes = Column(Text, nullable=True)
    result = Column(Text, nullable=True)

    # Relationships
    manager = relationship("Member", foreign_keys=[manager_id])
    attendances = relationship("Attendance", back_populates="activity", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="activity", cascade="all, delete-orphan")


class Attendance(Base):
    """Bảng attendances - Điểm danh"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    status = Column(String(20), default="absent")  # present, absent, excused

    # Relationships
    activity = relationship("Activity", back_populates="attendances")
    member = relationship("Member", back_populates="attendances")


class Task(Base):
    """Bảng tasks - Nhiệm vụ"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("members.id"), nullable=True)
    assigned_by = Column(Integer, ForeignKey("members.id"), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(30), default="not_started")  # not_started, in_progress, completed, overdue
    progress = Column(Integer, default=0)  # 0-100
    priority = Column(String(20), default="medium")  # low, medium, high, urgent

    # Relationships
    activity = relationship("Activity", back_populates="tasks")
    assignee = relationship("Member", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    assigner = relationship("Member", foreign_keys=[assigned_by])


class Notification(Base):
    """Bảng notifications - Thông báo"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="notifications")


class AIRequest(Base):
    """Bảng ai_requests - Lịch sử yêu cầu AI"""
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # notification, summarize, assign_task
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
