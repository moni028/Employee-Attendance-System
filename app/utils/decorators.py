from functools import wraps

from flask import abort
from flask_login import current_user

from app.models.enums import UserRole


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def employee_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.EMPLOYEE:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
