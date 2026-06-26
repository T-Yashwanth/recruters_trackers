"""
Gmail API OAuth 2.0 authentication module.

This module manages client credentials and authorization tokens for accessing
the Gmail API. It supports automatic token loading, validation, refreshing,
and running a local web server for authorization on the first run.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

# Scopes define the level of access requested from the Gmail API.
# - readonly: read emails and settings
# - modify: archive, trash, mark as read
# - send: send outgoing outreach emails
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_credentials():
    """
    Retrieves OAuth 2.0 credentials for Gmail API access.
    
    Checks for an existing 'token.json' file to authenticate silently. If it is
    absent or invalid, triggers a local server-based OAuth consent flow using
    'credentials.json'. Refreshes the token automatically if it has expired.
    
    Returns:
        google.oauth2.credentials.Credentials: Authorized user credentials.
    """
    creds = None
    # Resolve absolute paths relative to this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, "token.json")
    credentials_path = os.path.join(base_dir, "credentials.json")

    # Step 1: Attempt to load existing user access token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path,
            SCOPES
        )

    # Step 2: If credentials don't exist or are invalid, log the user in
    if not creds or not creds.valid:
        # If token expired but a refresh token is present, refresh it
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # Otherwise, initiate the full browser authorization flow
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Step 3: Save the newly acquired credentials for future runs
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds