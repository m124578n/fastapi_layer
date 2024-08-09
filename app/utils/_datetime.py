from datetime import datetime

import pytz

from app.config import TIMEZONE


def get_now():
    return datetime.now(pytz.timezone(TIMEZONE))
