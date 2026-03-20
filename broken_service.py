from datetime import datetime
from typing import Optional


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Safely parse a date string into a datetime object.
    Returns None if the string is empty, missing, or malformed.
    """
    if not date_string or not date_string.strip():
        return None
    try:
        return datetime.strptime(date_string.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def get_contacts_to_reach_out(contacts: list[dict], threshold: int = 30) -> list[dict]:
    """
    Returns contacts whose last contact date exceeds the threshold (in days).
    Handles missing dates, malformed dates, and edge cases.
    """
    result = []

    for contact in contacts:
        last_contacted = contact.get("last_contacted", "")
        parsed_date = parse_date(last_contacted)

        if parsed_date is None:
            # Missing or invalid date — flag for outreach
            result.append({
                **contact,
                "days_since_contact": None,
                "reason": "No valid last contact date"
            })
            continue

        days_since = (datetime.now() - parsed_date).days

        if days_since < 0:
            # Future date — skip, likely data error
            continue

        if days_since > threshold:
            result.append({
                **contact,
                "days_since_contact": days_since,
                "reason": f"Not contacted in {days_since} days"
            })

    return result