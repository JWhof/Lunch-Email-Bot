import datetime
import no_lunch_found
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

use_override_date = True
override_date = "2024-01-22"

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

    if lunch_items_list == []:
        raise no_lunch_found.NoLunchFoundError("No lunch could be found for this date.")
        

def create_lunch_items_dict() -> None:
    """Separates the items from lunch_items_list into keys and values in lunch_items dict. 
    Includes a try except if vegetarian hot lunch is not available."""


    global lunch_items_dict
    lunch_items_dict = {}

    lunch_items_dict["Soups"] = [lunch_item.strip() for lunch_item in lunch_items_list if "soup" in lunch_item.lower() and "soups" not in lunch_item.lower()]
    lunch_items_dict["Snack"] = lunch_items_list[next(i for i,v in enumerate(lunch_items_list) if v.lower() == 'hot snacks') + 1]
    lunch_items_dict["Lunch"] = lunch_items_list[next(i for i,v in enumerate(lunch_items_list) if v.lower() == 'hot lunch') + 1]
    
    try:
        lunch_items_dict["Veg Lunch"] = lunch_items_list[next(i for i,v in enumerate(lunch_items_list) if v.lower() == 'hot lunch (v)') + 1]
    except StopIteration:
        print("retrieved day is monday")

    print(lunch_items_dict)


if __name__ == "__main__":
    main()
    retrieve_correct_day_info()
    create_lunch_items_dict()
