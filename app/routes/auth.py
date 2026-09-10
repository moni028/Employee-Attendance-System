from urllib.parse import urljoin, urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.forms import LoginForm
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _is_safe_redirect(target):
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = db.session.scalar(
                db.select(User).where(or_(User.username == form.identity.data, User.email == form.identity.data))
            )
        except OperationalError:
            db.session.rollback()
            current_app.logger.exception("Database connection failed during login")
            flash("The database is unavailable. Check DATABASE_URL and PostgreSQL credentials.", "danger")
            return render_template("auth/login.html", form=form), 503
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_url = request.args.get("next")
            if _is_safe_redirect(next_url):
                return redirect(next_url)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials or inactive account.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
