from datetime import datetime, timezone

from app.extensions import db
from .enums import LeaveStatus, LeaveType


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    leave_type = db.Column(db.Enum(LeaveType, name="leave_type"), nullable=False)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(LeaveStatus, name="leave_status"), nullable=False, default=LeaveStatus.PENDING, index=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    admin_remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee = db.relationship("Employee", back_populates="leave_requests")
    approver = db.relationship("User", back_populates="approved_leave_requests", foreign_keys=[approved_by])
