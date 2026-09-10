from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms_employee import EmployeeForm, EmployeeUpdateForm
from app.models import Attendance, Department, Employee, LeaveRequest, User
from app.models.enums import EmployeeStatus, LeaveStatus, UserRole
from app.utils.decorators import admin_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/employees", methods=["GET", "POST"])
@login_required
@admin_required
def employees():
    form = EmployeeForm()
    departments = db.session.scalars(db.select(Department).order_by(Department.name)).all()
    if not departments:
        departments = [Department(name=name) for name in ("Administration", "Finance", "Human Resources", "Information Technology", "Operations")]
        db.session.add_all(departments)
        db.session.commit()
        flash("Default departments were added. You can now assign a department to the employee.", "info")
    form.department_id.choices = [(department.id, department.name) for department in departments]
    if form.validate_on_submit():
        existing = db.session.scalar(db.select(User).where(or_(User.username == form.username.data, User.email == form.email.data)))
        if existing or db.session.scalar(db.select(Employee).where(or_(Employee.employee_code == form.employee_code.data, Employee.email == form.email.data))):
            flash("The username, email, or employee code already exists.", "danger")
        else:
            user = User(username=form.username.data.strip(), email=form.email.data.strip().lower(), role=UserRole.EMPLOYEE)
            user.set_password(form.password.data)
            employee = Employee(
                employee_code=form.employee_code.data.strip(), user=user,
                first_name=form.first_name.data.strip(), last_name=form.last_name.data.strip(),
                email=form.email.data.strip().lower(), phone=form.phone.data.strip() or None,
                designation=form.designation.data.strip() or None, department_id=form.department_id.data,
                joining_date=form.joining_date.data,
                status=EmployeeStatus.ACTIVE,
            )
            db.session.add(employee)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("The employee could not be created because a unique value already exists.", "danger")
            else:
                flash("Employee account created successfully.", "success")
                return redirect(url_for("admin.employees"))
    elif form.is_submitted():
        for field in form:
            for error in field.errors:
                flash(f"{field.label.text}: {error}", "danger")

    employees = db.session.scalars(db.select(Employee).order_by(Employee.first_name, Employee.last_name)).all()
    return render_template("admin/employees.html", form=form, employees=employees, departments=departments)


@admin_bp.get("/employees/<int:employee_id>")
@login_required
@admin_required
def employee_detail(employee_id):
    employee = db.session.get(Employee, employee_id)
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("admin.employees"))

    attendance_records = db.session.scalars(
        db.select(Attendance)
        .where(Attendance.employee_id == employee.id)
        .order_by(Attendance.attendance_date.desc())
    ).all()
    leave_requests = db.session.scalars(
        db.select(LeaveRequest)
        .where(LeaveRequest.employee_id == employee.id)
        .order_by(LeaveRequest.created_at.desc())
    ).all()
    return render_template("admin/employee_detail.html", employee=employee, attendance_records=attendance_records, leave_requests=leave_requests)


@admin_bp.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = db.session.get(Employee, employee_id)
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("admin.employees"))

    departments = db.session.scalars(db.select(Department).order_by(Department.name)).all()
    form = EmployeeUpdateForm(obj=employee)
    form.username.data = employee.user.username
    form.department_id.choices = [(department.id, department.name) for department in departments]
    if form.validate_on_submit():
        duplicate_user = db.session.scalar(db.select(User).where(User.id != employee.user_id, or_(User.username == form.username.data, User.email == form.email.data)))
        duplicate_employee = db.session.scalar(db.select(Employee).where(Employee.id != employee.id, or_(Employee.employee_code == form.employee_code.data, Employee.email == form.email.data)))
        if duplicate_user or duplicate_employee:
            flash("The username, email, or employee code already exists.", "danger")
        else:
            employee.employee_code = form.employee_code.data.strip()
            employee.first_name = form.first_name.data.strip()
            employee.last_name = form.last_name.data.strip()
            employee.email = form.email.data.strip().lower()
            employee.phone = form.phone.data.strip() or None
            employee.designation = form.designation.data.strip() or None
            employee.department_id = form.department_id.data
            employee.joining_date = form.joining_date.data
            employee.user.username = form.username.data.strip()
            employee.user.email = form.email.data.strip().lower()
            db.session.commit()
            flash("Employee details updated successfully.", "success")
            return redirect(url_for("admin.employee_detail", employee_id=employee.id))
    return render_template("admin/employee_edit.html", form=form, employee=employee)


@admin_bp.post("/employees/<int:employee_id>/delete")
@login_required
@admin_required
def delete_employee(employee_id):
    employee = db.session.get(Employee, employee_id)
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("admin.employees"))

    user = employee.user
    db.session.query(Attendance).filter_by(employee_id=employee.id).delete(synchronize_session=False)
    db.session.query(LeaveRequest).filter_by(employee_id=employee.id).delete(synchronize_session=False)
    db.session.delete(employee)
    db.session.flush()
    db.session.delete(user)
    db.session.commit()
    flash("Employee and related records deleted successfully.", "success")
    return redirect(url_for("admin.employees"))


@admin_bp.get("/attendance")
@login_required
@admin_required
def attendance():
    records = db.session.scalars(db.select(Attendance).order_by(Attendance.attendance_date.desc(), Attendance.check_in.desc())).all()
    return render_template("admin/attendance.html", records=records)


@admin_bp.get("/reports")
@login_required
@admin_required
def reports():
    return redirect(url_for("dashboard"))


@admin_bp.get("/leaves")
@login_required
@admin_required
def leaves():
    requests = db.session.scalars(db.select(LeaveRequest).order_by(LeaveRequest.created_at.desc())).all()
    return render_template("admin/leaves.html", requests=requests)


@admin_bp.post("/leaves/<int:request_id>/<decision>")
@login_required
@admin_required
def decide_leave(request_id, decision):
    leave_request = db.session.get(LeaveRequest, request_id)
    if not leave_request:
        flash("Leave request not found.", "danger")
        return redirect(url_for("admin.leaves"))
    if decision not in {"approve", "reject"}:
        flash("Invalid leave decision.", "danger")
        return redirect(url_for("admin.leaves"))
    if leave_request.status != LeaveStatus.PENDING:
        flash("This leave request has already been decided.", "warning")
        return redirect(url_for("admin.leaves"))

    leave_request.status = LeaveStatus.APPROVED if decision == "approve" else LeaveStatus.REJECTED
    leave_request.approved_by = current_user.id
    leave_request.admin_remarks = "Approved by administrator." if decision == "approve" else "Rejected by administrator."
    db.session.commit()
    flash(f"Leave request {leave_request.status.value.lower()}.", "success")
    return redirect(url_for("admin.leaves"))


