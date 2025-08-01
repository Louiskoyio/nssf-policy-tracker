# utils.py
from datetime import datetime

def format_date(date_value):
    try:
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
        elif isinstance(date_value, (datetime,)):
            date_obj = date_value
        else:
            return str(date_value)  # fallback

        day = date_obj.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return date_obj.strftime(f"{day}{suffix} %B %Y")

    except Exception as e:
        return str(date_value)
