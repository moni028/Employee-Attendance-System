from flask import Flask, jsonify, render_template
from flask_login import current_user, login_required

from config import Config
from .extensions import csrf, db, login_manager, migrate
from . import models
from .cli import create_admin
from .routes.auth import auth_bp
from .routes.attendance import attendance_bp
from .routes.admin import admin_bp
from .routes.employee import employee_bp
from .models.enums import AttendanceStatus, LeaveStatus, UserRole
from .utils.time import local_now, local_time, local_today


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    @app.context_processor
    def office_schedule():
        now = local_now()
        return {
            "office_start_time": app.config["OFFICE_START_TIME"].strftime("%I:%M %p"),
            "office_end_time": app.config["OFFICE_END_TIME"].strftime("%I:%M %p"),
            "current_date": f"{now:%A}, {now:%B} {now.day}, {now:%Y}",
            "current_time": now.strftime("%I:%M %p"),
            "local_time": local_time,
        }

    login_manager.user_loader(lambda user_id: db.session.get(models.User, int(user_id)))
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_bp)
    app.cli.add_command(create_admin)

    @app.get("/")
    @login_required
    def dashboard():
        if current_user.role == UserRole.EMPLOYEE:
            attendance = None
            if current_user.employee:
                attendance = db.session.scalar(
                    db.select(models.Attendance).where(
                        models.Attendance.employee_id == current_user.employee.id,
                        models.Attendance.attendance_date == local_today(),
                    )
                )
            return render_template("employee_dashboard.html", attendance=attendance)

        today = local_today()
        stats = {
            "total_employees": db.session.scalar(db.select(db.func.count()).select_from(models.Employee)) or 0,
            "present_today": db.session.scalar(db.select(db.func.count()).select_from(models.Attendance).where(
                models.Attendance.attendance_date == today,
                models.Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.HALF_DAY]),
            )) or 0,
            "late_today": db.session.scalar(db.select(db.func.count()).select_from(models.Attendance).where(
                models.Attendance.attendance_date == today,
                models.Attendance.status == AttendanceStatus.LATE,
            )) or 0,
            "pending_leaves": db.session.scalar(db.select(db.func.count()).select_from(models.LeaveRequest).where(
                models.LeaveRequest.status == LeaveStatus.PENDING,
            )) or 0,
        }
        recent_attendance = db.session.scalars(db.select(models.Attendance).where(models.Attendance.attendance_date == today).order_by(models.Attendance.check_in.desc())).all()
        pending_leave_requests = db.session.scalars(db.select(models.LeaveRequest).where(models.LeaveRequest.status == LeaveStatus.PENDING).order_by(models.LeaveRequest.created_at.desc())).all()
        return render_template("dashboard.html", stats=stats, recent_attendance=recent_attendance, pending_leave_requests=pending_leave_requests)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "employee-attendance"})

    return app
