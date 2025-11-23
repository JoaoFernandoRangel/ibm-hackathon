"""Demo script to exercise the orchestrate follow-up workflow.

This script demonstrates calling `orchestrate_followup_workflow`.
Replace `ACCESS_TOKEN` with a valid Gmail OAuth access token with `https://www.googleapis.com/auth/gmail.send` scope.
"""
from src.orchestrate_tools import (
    OrchestrateFollowupInput,
    orchestrate_followup_workflow,
)

ACCESS_TOKEN = "REPLACE_WITH_VALID_GMAIL_OAUTH_ACCESS_TOKEN"

def main():
    inp = OrchestrateFollowupInput(
        patient_email="patient@example.com",
        form_link="https://example.com/followup-form",
        followup_subject="Follow-up: Please complete the short form",
        followup_body_template="Hello, please complete the follow-up form here: {form_link}\n\nBest regards, Clinic",
        schedule=True,
        start_iso="2025-12-01T10:00:00Z",
        end_iso="2025-12-01T10:30:00Z",
        organizer_email="clinic@example.com",
        access_token=ACCESS_TOKEN,
    )

    result = orchestrate_followup_workflow(inp)
    print("Orchestration result:\n", result)


if __name__ == '__main__':
    main()
