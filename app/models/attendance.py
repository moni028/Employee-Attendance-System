from datetime import datetime, timezone

from app.extensions import db
from .enums import AttendanceStatus


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (db.UniqueConstraint("employee_id", "attendance_date", name="uq_attendance_employee_date"),)

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.DateTime(timezone=True))
    check_out = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.Enum(AttendanceStatus, name="attendance_status"), nullable=False, index=True)
    working_hours = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    employee = db.relationship("Employee", back_populates="attendance_records")
