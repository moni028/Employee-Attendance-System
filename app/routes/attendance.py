from flask import Blueprint, flash, jsonify, redirect, url_for
from flask_login import current_user, login_required

from app.services.attendance_service import AttendanceError, check_in, check_out


attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


def _employee_required():
    if not current_user.employee:
        return jsonify({"error": "Employee profile is required."}), 403
    return None


@attendance_bp.post("/check-in")
@login_required
def employee_check_in():
    profile_error = _employee_required()
    if profile_error:
        return profile_error
    try:
        attendance = check_in(current_user.employee)
    except AttendanceError as error:
        return jsonify({"error": str(error)}), 400
    flash("Checked in successfully.", "success")
    return redirect(url_for("dashboard"))


@attendance_bp.post("/check-out")
@login_required
def employee_check_out():
    profile_error = _employee_required()
    if profile_error:
        return profile_error
    try:
        attendance = check_out(current_user.employee)
    except AttendanceError as error:
        return jsonify({"error": str(error)}), 400
    flash(f"Checked out successfully. Working hours: {attendance.working_hours}.", "success")
    return redirect(url_for("dashboard"))


@attendance_bp.get("/today")
@login_required
def today_attendance():
    profile_error = _employee_required()
    if profile_error:
        return profile_error
    from datetime import date
    from app.extensions import db
    from app.models import Attendance

    attendance = db.session.scalar(
        db.select(Attendance).where(
            Attendance.employee_id == current_user.employee.id,
            Attendance.attendance_date == date.today(),
        )
    )
    if not attendance:
        return jsonify({"attendance": None})
    return jsonify({
        "attendance": {
            "date": attendance.attendance_date.isoformat(),
            "check_in": attendance.check_in.isoformat() if attendance.check_in else None,
            "check_out": attendance.check_out.isoformat() if attendance.check_out else None,
            "status": attendance.status.value,
            "working_hours": str(attendance.working_hours),
            "overtime_hours": str(attendance.overtime_hours),
        }
    })
