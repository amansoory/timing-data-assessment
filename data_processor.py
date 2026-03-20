import csv
import logging
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Priority rankings — lower number = higher priority
PRIORITY_MAP = {
    "investor": 1,
    "mentor": 2,
    "advisor": 3,
    "friend": 4,
}
DEFAULT_PRIORITY = 5


def load_contacts(filepath: str) -> list[dict]:
    """Load contacts from a CSV file."""
    contacts = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append(row)
        logger.info(f"Loaded {len(contacts)} contacts from {filepath}")
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
    return contacts


def parse_date(date_string: str) -> Optional[datetime]:
    """Safely parse a date string."""
    if not date_string or not date_string.strip():
        return None
    try:
        return datetime.strptime(date_string.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def get_priority(notes: str) -> int:
    """Return priority rank based on notes field."""
    if not notes:
        return DEFAULT_PRIORITY
    notes_lower = notes.strip().lower()
    return PRIORITY_MAP.get(notes_lower, DEFAULT_PRIORITY)


def get_top_contacts(contacts: list[dict], top_n: int = 2) -> tuple[list[dict], list[dict]]:
    """
    Returns top N priority contacts that should be contacted today.
    Contacts with missing dates are flagged separately.

    Sorting rules:
    1. Priority rank (investor > mentor > advisor > friend > other)
    2. Tie-breaker: longest time since last contact
    """
    today = datetime.now()
    scored = []
    missing_date = []

    for contact in contacts:
        parsed_date = parse_date(contact.get("last_contacted", ""))

        if parsed_date is None:
            missing_date.append({
                "name": contact["name"],
                "email": contact.get("email", ""),
                "notes": contact.get("notes", ""),
                "reason": "No valid last contact date on file"
            })
            continue

        days_since = (today - parsed_date).days

        if days_since < 0:
            logger.warning(f"Future date for {contact['name']} — skipping")
            continue

        priority = get_priority(contact.get("notes", ""))

        scored.append({
            "name": contact["name"],
            "email": contact.get("email", ""),
            "notes": contact.get("notes", ""),
            "priority_rank": priority,
            "days_since_contact": days_since,
        })

    # Sort: priority rank ASC, then days since contact DESC
    scored.sort(key=lambda x: (x["priority_rank"], -x["days_since_contact"]))

    return scored[:top_n], missing_date


def display_results(contacts: list[dict], missing: list[dict]) -> None:
    """Display top contacts and flag missing data."""
    if not contacts and not missing:
        print("No contacts to display.")
        return

    print("\n" + "=" * 55)
    print("  TOP PRIORITY CONTACTS TO REACH OUT TO")
    print("=" * 55)

    for i, contact in enumerate(contacts, 1):
        role = contact["notes"].capitalize() if contact["notes"] else "Other"
        days = contact["days_since_contact"]
        print(f"\n  {i}. {contact['name']}")
        print(f"     Role:    {role}")
        print(f"     Email:   {contact['email']}")
        print(f"     Last contacted: {days} days ago")

    if missing:
        print("\n" + "-" * 55)
        print("  DATA QUALITY FLAGS — Missing contact dates:")
        print("-" * 55)
        for contact in missing:
            role = contact["notes"].capitalize() if contact["notes"] else "Other"
            print(f"\n  - {contact['name']} ({role})")
            print(f"    {contact['reason']}")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    contacts = load_contacts("contacts.csv")
    top, missing = get_top_contacts(contacts, top_n=2)
    display_results(top, missing)