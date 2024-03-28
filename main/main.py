import datetime
import dateutil.parser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import no_lunch_found
import re

use_override_date = True
override_date = "2024-03-28"



def main():
    global events

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    creds = Credentials.from_authorized_user_file("secret/token.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = (
        service.events()
        .list(
            calendarId="nij10q76sud67hkgebrhs7nboil1gsld@import.calendar.google.com",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])




def retrieve_correct_day_info() -> None:
    """Retrieves the current day/override day's lunch menu and stores it in lunch_items list. 
    Throws NoLunchFoundError if there is no lunch available on that day (likely a weekend/holiday)."""

    global lunch_items_list

    lunch_items_list = []

    if use_override_date:
        for event in events:
            if str(event["start"].get("dateTime", event["start"].get("date"))) == override_date and "ES" not in event["summary"]:
                lunch_items_list = [line for line in event["description"].split("\n") if line != ""]
    else:
        for event in events:
            if str(event["start"].get("dateTime", event["start"].get("date"))) == str(datetime.datetime.utcnow().isoformat(timespec="hours").split("T")[0]) and "ES" not in event["summary"]:
                lunch_items_list = [line for line in event["description"].split("\n") if line != ""]
    lunch_items_list = [lunch_item.strip() for lunch_item in lunch_items_list]

    print(lunch_items_list)

    if lunch_items_list == []:
        raise no_lunch_found.NoLunchFoundError("No lunch could be found for this date.")
        

def create_lunch_items_dict(day) -> None:
    """Separates the items from lunch_items_list into keys and values in lunch_items dict. 
    Includes a try except if vegetarian hot lunch is not available."""

    global lunch_items_dict
    lunch_items_dict = {}

    soup_regex_pattern = r'\b[sS][oO][uU][pP][sS]\s*:?\s*'
    snack_regex_pattern = r'\b[hH][oO][tT]\s+[sS][nN][aA][cC][kK][sS]?\s*:?\s*'
    lunch_regex_pattern = r'\b[hH][oO][tT]\s+[lL][uU][nN][cC][hH]\s*:?\s*'

    lunch_items_dict["Soups"] = re.sub(soup_regex_pattern, '', lunch_items_list[0], count=1)
    lunch_items_dict["Snack"] = re.sub(snack_regex_pattern, '', lunch_items_list[1], count=1)
    lunch_items_dict["Lunch"] = re.sub(lunch_regex_pattern, '', lunch_items_list[2], count=1)
    
    if is_day_monday(day):
        print("day is monday")
    else:
        print("day is not monday")

    print(lunch_items_dict)
    

def is_day_monday(day) -> bool:
    event_day = dateutil.parser.parse(day)
    day_of_week = event_day.weekday()
    if day_of_week == 0:
        return True
    return False


if __name__ == "__main__":
    main()
