from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


def local_now():
    return datetime.now(ZoneInfo(current_app.config["TIMEZONE"]))


def local_today():
    return local_now().date()