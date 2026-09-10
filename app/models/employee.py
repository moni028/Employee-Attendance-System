from datetime import datetime, timezone

from app.extensions import db
from .enums import EmployeeStatus


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), index=True)
    designation = db.Column(db.String(120))
    joining_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(EmployeeStatus, name="employee_status"), nullable=False, default=EmployeeStatus.ACTIVE, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="employee")
    department = db.relationship("Department", back_populates="employees")
    attendance_records = db.relationship("Attendance", back_populates="employee")
    leave_requests = db.relationship("LeaveRequest", back_populates="employee")
