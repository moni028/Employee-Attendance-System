from datetime import datetime, timezone

from flask import current_app
from sqlalchemy.types import TypeDecorator
from zoneinfo import ZoneInfo

from app.extensions import db
from .enums import AttendanceStatus


class LocalDateTime(TypeDecorator):
    impl = db.DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo(current_app.config["TIMEZONE"]))
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(ZoneInfo(current_app.config["TIMEZONE"]))


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (db.UniqueConstraint("employee_id", "attendance_date", name="uq_attendance_employee_date"),)

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(LocalDateTime())
    check_out = db.Column(LocalDateTime())
    status = db.Column(db.Enum(AttendanceStatus, name="attendance_status"), nullable=False, index=True)
    working_hours = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee = db.relationship("Employee", back_populates="attendance_records")
