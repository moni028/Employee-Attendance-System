from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from flask import current_app

from app.extensions import db
from app.models import Attendance, Holiday, LeaveRequest
from app.models.enums import AttendanceStatus, EmployeeStatus, LeaveStatus


class AttendanceError(ValueError):
    """Raised when an attendance action violates a business rule."""


def _localize(timestamp):
    timezone = ZoneInfo(current_app.config["TIMEZONE"])
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone)
    return timestamp.astimezone(timezone)


def _hours_between(start, end):
    seconds = Decimal((end - start).total_seconds())
    return (seconds / Decimal("3600")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _is_non_working_day(employee_id, attendance_date):
    holiday = db.session.scalar(db.select(Holiday).where(Holiday.holiday_date == attendance_date))
    if holiday:
        return AttendanceStatus.HOLIDAY

    approved_leave = db.session.scalar(
        db.select(LeaveRequest).where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveRequest.start_date <= attendance_date,
            LeaveRequest.end_date >= attendance_date,
        )
    )
    if approved_leave:
        return AttendanceStatus.LEAVE
    return None


def check_in(employee, timestamp=None):
    if employee.status != EmployeeStatus.ACTIVE or not employee.user.is_active:
        raise AttendanceError("Inactive employees cannot record attendance.")

    checked_at = _localize(timestamp or datetime.now(ZoneInfo(current_app.config["TIMEZONE"])))
    attendance_date = checked_at.date()
    non_working_status = _is_non_working_day(employee.id, attendance_date)
    if non_working_status:
        raise AttendanceError(f"Attendance cannot be recorded on a {non_working_status.value.lower()} day.")

    attendance = db.session.scalar(
        db.select(Attendance).where(
            Attendance.employee_id == employee.id,
            Attendance.attendance_date == attendance_date,
        )
    )
    if attendance and attendance.check_in:
        raise AttendanceError("You have already checked in today.")

    start_time = current_app.config["OFFICE_START_TIME"]
    late_at = datetime.combine(attendance_date, start_time) + timedelta(
        minutes=current_app.config["LATE_THRESHOLD_MINUTES"]
    )
    status = AttendanceStatus.LATE if checked_at.replace(tzinfo=None) > late_at else AttendanceStatus.PRESENT

    if attendance is None:
        attendance = Attendance(employee_id=employee.id, attendance_date=attendance_date, status=status)
        db.session.add(attendance)
    else:
        attendance.status = status
    attendance.check_in = checked_at
    db.session.commit()
    return attendance


def check_out(employee, timestamp=None):
    if employee.status != EmployeeStatus.ACTIVE or not employee.user.is_active:
        raise AttendanceError("Inactive employees cannot record attendance.")

    checked_at = _localize(timestamp or datetime.now(ZoneInfo(current_app.config["TIMEZONE"])))
    attendance = db.session.scalar(
        db.select(Attendance).where(
            Attendance.employee_id == employee.id,
            Attendance.attendance_date == checked_at.date(),
        )
    )
    if not attendance or not attendance.check_in:
        raise AttendanceError("Check in before checking out.")
    if attendance.check_out:
        raise AttendanceError("You have already checked out today.")

    attendance.check_out = checked_at
    attendance.working_hours = _hours_between(_localize(attendance.check_in), checked_at)
    standard_hours = Decimal(str(current_app.config["STANDARD_WORKING_HOURS"]))
    attendance.overtime_hours = max(Decimal("0"), attendance.working_hours - standard_hours)
    if attendance.working_hours < Decimal(str(current_app.config["HALF_DAY_THRESHOLD_HOURS"])):
        attendance.status = AttendanceStatus.HALF_DAY
    db.session.commit()
    return attendance
