from datetime import datetime
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import no_lunch_found
import re

use_override_date = True
override_date = "2024-03-28"
API_KEY = open("secret/mailgun_api_key.txt", "r").read()
DOMAIN_NAME = "sandbox9f74cd3c9c8943feaba6c15f177944d0.mailgun.org"
USER_LIST = ["jwesterhof@ash.nl"]

class LunchBot:
    def __init__(self):
        self.events = None
        self.event_day = None
        self.lunch_items_list = []
        self.lunch_items_dict = {}
        self.api_key = API_KEY
        self.domain_name = DOMAIN_NAME

    def setup(self):
        SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
        creds = Credentials.from_authorized_user_file("secret/token.json", SCOPES)
        service = build("calendar", "v3", credentials=creds)
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
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
        self.events = events_result.get("items", [])

    def retrieve_day_info(self) -> None:
        """Retrieves the current day/override day's lunch menu and stores it in lunch_items list. 
    Throws NoLunchFoundError if there is no lunch available on that day (likely a weekend/holiday)."""
        if use_override_date:
            for event in self.events:
                if str(event["start"].get("dateTime", event["start"].get("date"))) == override_date and "ES" not in event["summary"]:
                    self.event_day = str(event["start"].get("dateTime", event["start"].get("date")))
                    self.lunch_items_list = [line for line in event["description"].split("\n") if line != ""]
        else:
            for event in self.events:
                if str(event["start"].get("dateTime", event["start"].get("date"))) == str(datetime.utcnow().isoformat(timespec="hours").split("T")[0]) and "ES" not in event["summary"]:
                    self.event_day = str(event["start"].get("dateTime", event["start"].get("date")))
                    self.lunch_items_list = [line for line in event["description"].split("\n") if line != ""]
        self.lunch_items_list = [lunch_item.strip() for lunch_item in self.lunch_items_list]

        if self.lunch_items_list == []:
            raise no_lunch_found.NoLunchFoundError("No lunch could be found for this date.")
    
    def init_menu_dict(self) -> None:
        """Separates the items from lunch_items_list into keys and values in lunch_items dict. 
        Includes a try except if vegetarian hot lunch is not available."""
        soup_regex_pattern = r'\b[sS][oO][uU][pP][sS]\s*:?\s*'
        snack_regex_pattern = r'\b[hH][oO][tT]\s+[sS][nN][aA][cC][kK][sS]?\s*:?\s*'
        lunch_regex_pattern = r'\b[hH][oO][tT]\s+[lL][uU][nN][cC][hH]\s*:?\s*'

        self.lunch_items_dict["Soups"] = re.sub(soup_regex_pattern, '', self.lunch_items_list[0], count=1)
        self.lunch_items_dict["Snack"] = re.sub(snack_regex_pattern, '', self.lunch_items_list[1], count=1)
        self.lunch_items_dict["Lunch"] = re.sub(lunch_regex_pattern, '', self.lunch_items_list[2], count=1)

        if not self.is_day_monday():
            veg_lunch_regex_pattern = r'\b[hH][oO][tT]\s+[lL][uU][nN][cC][hH]\s*\([vV]\)\s*:?\s*'
            self.lunch_items_dict["Veg Lunch"] = re.sub(veg_lunch_regex_pattern, '', self.lunch_items_list[3], count=1)
    
    def is_day_monday(self) -> bool:
        """Returns if the day is monday or not."""
        date_obj = datetime.strptime(self.event_day, "%Y-%m-%d")
        self.weekday = date_obj.weekday()
        return self.weekday == 0

    def send_email(self) -> int:
        return requests.post(
		f"https://api.mailgun.net/v3/{self.domain_name}/messages",
		auth=("api", f"{self.api_key}"),
		data={"from": f"Lunch Menu Bot<lunch@{self.domain_name}>",
			"to": USER_LIST,
			"subject": f"{self.lunch_items_dict['Lunch']}, {self.lunch_items_dict['Snack']}, {self.lunch_items_dict['Soups']}",
			"text": "Test"}).status_code

bot = LunchBot()
bot.setup()
bot.retrieve_day_info()
bot.init_menu_dict()
print(bot.send_email())