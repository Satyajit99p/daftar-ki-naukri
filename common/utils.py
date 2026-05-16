from datetime import datetime, timezone
from dateutil import parser



from datetime import datetime, timezone
from dateutil import parser
import re

def parse_timestamp(value):
    if not value:
        return None

    cleaned = value.strip().strip(".")

    if not cleaned or cleaned.lower() in {"na", "n/a", "-"}:
        return None

    if "/" in cleaned and any(char.isalpha() for char in cleaned):
        return None

    # Add missing space after comma
    cleaned = re.sub(r",(\d)", r", \1", cleaned)

    try:
        # If month name exists, don't use dayfirst
        has_text_month = any(char.isalpha() for char in cleaned)

        parsed = parser.parse(
            cleaned,
            dayfirst=not has_text_month
        )

        today = datetime.now(timezone.utc).date()

        if parsed.date() > today:
            print(f"Warning: Parsed date {parsed.date()} is in the future. Original value: '{value}'")

        return parsed.isoformat()

    except Exception:
        return None


