import uuid
from datetime import datetime
import base64
from pydantic import BaseModel
from typing import Optional

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

from .send_email_tool import (
    send_gmail_email,
    GmailSendInput,
    send_gmail_email_with_ics,
    GmailSendWithAttachmentInput,
)


def _format_dt_to_utc_str(dt: datetime) -> str:
    """Format a datetime to ICS/UTC timestamp: YYYYMMDDTHHMMSSZ"""
    return dt.utcnow().strftime('%Y%m%dT%H%M%SZ') if dt.tzinfo is None else dt.astimezone(tz=None).strftime('%Y%m%dT%H%M%SZ')


def create_ics_event(subject: str, start_iso: str, end_iso: str, description: str, organizer_email: str, attendee_email: str) -> str:
    """Create a simple ICS calendar event as a string.

    - `start_iso` and `end_iso` should be ISO-8601 strings (e.g., 2025-11-22T15:00:00Z).
    - Returns the ICS file content as text.
    """
    try:
        start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_iso.replace('Z', '+00:00'))
    except Exception:
        # fallback: parse naive
        start_dt = datetime.fromisoformat(start_iso)
        end_dt = datetime.fromisoformat(end_iso)

    dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    uid = str(uuid.uuid4())

    # Use UTC timestamps
    def _fmt(dt: datetime) -> str:
        return dt.strftime('%Y%m%dT%H%M%SZ')

    ics = (
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//ibm-hackathon//EN\r\n'
        'CALSCALE:GREGORIAN\r\n'
        'METHOD:REQUEST\r\n'
        'BEGIN:VEVENT\r\n'
        f'UID:{uid}\r\n'
        f'DTSTAMP:{dtstamp}\r\n'
        f'DTSTART:{_fmt(start_dt)}\r\n'
        f'DTEND:{_fmt(end_dt)}\r\n'
        f'SUMMARY:{subject}\r\n'
        f'DESCRIPTION:{description}\r\n'
        f'ORGANIZER:MAILTO:{organizer_email}\r\n'
        f'ATTENDEE;CN=Patient;RSVP=TRUE:MAILTO:{attendee_email}\r\n'
        'END:VEVENT\r\n'
        'END:VCALENDAR\r\n'
    )

    return ics


class FollowupEmailInput(BaseModel):
    patient_email: str
    subject: str
    body: str
    access_token: str


@tool(permission=ToolPermission.WRITE_ONLY, description="Send a follow-up form link to a patient via Gmail")
def send_followup_email(input: FollowupEmailInput) -> str:
    payload = GmailSendInput(
        to=input.patient_email,
        subject=input.subject,
        body=input.body,
        access_token=input.access_token,
    )
    return send_gmail_email(payload)


class ScheduleAppointmentInput(BaseModel):
    patient_email: str
    subject: str
    description: str
    start_iso: str
    end_iso: str
    organizer_email: str
    access_token: str
    ics_filename: Optional[str] = 'invite.ics'


@tool(permission=ToolPermission.WRITE_ONLY, description="Schedule appointment by sending an ICS invite via Gmail")
def schedule_appointment_ics(input: ScheduleAppointmentInput) -> str:
    ics = create_ics_event(
        subject=input.subject,
        start_iso=input.start_iso,
        end_iso=input.end_iso,
        description=input.description,
        organizer_email=input.organizer_email,
        attendee_email=input.patient_email,
    )

    ics_b64 = base64.b64encode(ics.encode('utf-8')).decode('utf-8')

    payload = GmailSendWithAttachmentInput(
        to=input.patient_email,
        subject=input.subject,
        body=input.description,
        access_token=input.access_token,
        attachment_bytes_base64=ics_b64,
        attachment_filename=input.ics_filename,
    )

    return send_gmail_email_with_ics(payload)


class OrchestrateFollowupInput(BaseModel):
    patient_email: str
    form_link: str
    followup_subject: str
    followup_body_template: str
    schedule: bool = False
    start_iso: Optional[str] = None
    end_iso: Optional[str] = None
    organizer_email: Optional[str] = None
    access_token: str


@tool(permission=ToolPermission.WRITE_ONLY, description="Composite workflow: send follow-up form link and optionally schedule an appointment")
def orchestrate_followup_workflow(input: OrchestrateFollowupInput) -> dict:
    # Send follow-up email
    body = input.followup_body_template.replace("{form_link}", input.form_link)
    send_payload = FollowupEmailInput(
        patient_email=input.patient_email,
        subject=input.followup_subject,
        body=body,
        access_token=input.access_token,
    )
    send_result = send_followup_email(send_payload)

    schedule_result = None
    if input.schedule and input.start_iso and input.end_iso and input.organizer_email:
        sched_payload = ScheduleAppointmentInput(
            patient_email=input.patient_email,
            subject='Appointment: ' + input.followup_subject,
            description=body,
            start_iso=input.start_iso,
            end_iso=input.end_iso,
            organizer_email=input.organizer_email,
            access_token=input.access_token,
        )
        schedule_result = schedule_appointment_ics(sched_payload)

    return {
        'email_sent_subject': send_result,
        'schedule_result': schedule_result,
    }
