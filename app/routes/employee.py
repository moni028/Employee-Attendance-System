from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms_employee import LeaveRequestForm
from app.models import Attendance, LeaveRequest
from app.models.enums import LeaveStatus, LeaveType
from app.utils.decorators import employee_required


employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


@employee_bp.get("/attendance")
@login_required
@employee_required
def attendance_history():
    records = db.session.scalars(db.select(Attendance).where(Attendance.employee_id == current_user.employee.id).order_by(Attendance.attendance_date.desc())).all()
    return render_template("employee/attendance.html", records=records)


@employee_bp.route("/leave", methods=["GET", "POST"])
@login_required
@employee_required
def leave_history():
    form = LeaveRequestForm()
    if form.validate_on_submit():
        request = LeaveRequest(employee_id=current_user.employee.id, leave_type=LeaveType(form.leave_type.data), start_date=form.start_date.data, end_date=form.end_date.data, reason=form.reason.data.strip(), status=LeaveStatus.PENDING)
        db.session.add(request)
        db.session.commit()
        flash("Your leave request has been submitted.", "success")
        return redirect(url_for("employee.leave_history"))
    requests = db.session.scalars(db.select(LeaveRequest).where(LeaveRequest.employee_id == current_user.employee.id).order_by(LeaveRequest.created_at.desc())).all()
    return render_template("employee/leave.html", form=form, requests=requests)
