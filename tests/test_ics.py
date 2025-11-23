import re
from src.orchestrate_tools import create_ics_event


def test_create_ics_event_basic():
    subject = "Test Appointment"
    start = "2025-12-01T10:00:00Z"
    end = "2025-12-01T10:30:00Z"
    description = "This is a test."
    organizer = "clinic@example.com"
    attendee = "patient@example.com"

    ics = create_ics_event(subject, start, end, description, organizer, attendee)

    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert f"SUMMARY:{subject}" in ics
    assert re.search(r"DTSTART:\d{8}T\d{6}Z", ics)
    assert re.search(r"DTEND:\d{8}T\d{6}Z", ics)
    assert "UID:" in ics
    assert f"ORGANIZER:MAILTO:{organizer}" in ics
    assert f"MAILTO:{attendee}" in ics
