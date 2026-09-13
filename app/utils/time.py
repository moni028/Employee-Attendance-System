from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


def local_now():
    return datetime.now(ZoneInfo(current_app.config["TIMEZONE"]))


def local_today():
    return local_now().date()


def local_time(value, format_string="%I:%M %p"):
    if value is None:
        return "--"
    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo("UTC"))
    return value.astimezone(ZoneInfo(current_app.config["TIMEZONE"])).strftime(format_string)