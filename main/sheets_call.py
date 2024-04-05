from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def call():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    SPREADSHEET_ID = "1Y6uZBQ2reuLf04A73XAegEsR8UTbjWOzXPSM1SCSTEU"
    SPREADSHEET_RANGE = "Form Responses 1!A2:E"
    creds = Credentials.from_authorized_user_file("sheets_token.json", SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SPREADSHEET_RANGE)
        .execute()
    )
    print (", ".join([row[1] for row in result.get("values", [])]))