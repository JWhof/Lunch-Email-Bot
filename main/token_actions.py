from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def create_token() -> None:
    """Creates a new token. Used to prevent any token expiry issues."""
    flow = InstalledAppFlow.from_client_secrets_file(
            "secret/credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)
    with open("secret/token.json", "w") as token:
        token.write(creds.to_json())

def delete_token() -> None:
    """Deletes token.json. Prevents any issues arising regarding token expiry."""
    os.remove("secret/token.json")