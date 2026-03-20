import pytest
from datetime import datetime, timedelta
from broken_service import get_contacts_to_reach_out, parse_date


# ---- Tests for parse_date ----

class TestParseDate:
    def test_valid_date(self):
        result = parse_date("2024-01-10")
        assert result == datetime(2024, 1, 10)

    def test_empty_string(self):
        assert parse_date("") is None

    def test_none_input(self):
        assert parse_date(None) is None

    def test_malformed_date(self):
        assert parse_date("not-a-date") is None

    def test_whitespace_only(self):
        assert parse_date("   ") is None

    def test_wrong_format(self):
        assert parse_date("01/10/2024") is None


# ---- Tests for get_contacts_to_reach_out ----

class TestGetContactsToReachOut:
    def test_contact_over_30_days(self):
        """Core bug catch — contact over threshold should be returned."""
        old_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        contacts = [{"name": "Test User", "email": "test@test.com", "last_contacted": old_date, "notes": ""}]
        result = get_contacts_to_reach_out(contacts)
        assert len(result) == 1
        assert result[0]["name"] == "Test User"
        assert result[0]["days_since_contact"] >= 60

    def test_contact_under_30_days(self):
        """Recent contact should NOT be returned."""
        recent_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        contacts = [{"name": "Recent User", "email": "r@test.com", "last_contacted": recent_date, "notes": ""}]
        result = get_contacts_to_reach_out(contacts)
        assert len(result) == 0

    def test_missing_date(self):
        """Empty date should still return contact with reason."""
        contacts = [{"name": "No Date", "email": "nd@test.com", "last_contacted": "", "notes": "mentor"}]
        result = get_contacts_to_reach_out(contacts)
        assert len(result) == 1
        assert result[0]["days_since_contact"] is None
        assert "No valid" in result[0]["reason"]

    def test_future_date_skipped(self):
        """Future dates should be skipped."""
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        contacts = [{"name": "Future", "email": "f@test.com", "last_contacted": future_date, "notes": ""}]
        result = get_contacts_to_reach_out(contacts)
        assert len(result) == 0

    def test_missing_key(self):
        """Contact with no last_contacted key should not crash."""
        contacts = [{"name": "No Key", "email": "nk@test.com", "notes": ""}]
        result = get_contacts_to_reach_out(contacts)
        assert len(result) == 1

    def test_custom_threshold(self):
        """Custom threshold should be respected."""
        old_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
        contacts = [{"name": "Custom", "email": "c@test.com", "last_contacted": old_date, "notes": ""}]
        result = get_contacts_to_reach_out(contacts, threshold=10)
        assert len(result) == 1

    def test_empty_contact_list(self):
        """Empty list should return empty list."""
        assert get_contacts_to_reach_out([]) == []

    def test_exactly_30_days(self):
        """Exactly 30 days should NOT be returned (must exceed threshold)."""
        exact_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        contacts = [{"name": "Edge", "email": "e@test.com", "last_contacted": exact_date, "notes": ""}]
        result = get_contacts_to_reach_out(contacts)
        assert len(result) == 0