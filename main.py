import datetime
import os.path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        for start, end in parse_events("./events.txt"):
            event = {
                "summary": "Conduite",
                "description": "Conduite",
                "start": {
                    "dateTime": start.isoformat(),
                    "timeZone": "Europe/Paris",
                },
                "end": {
                    "dateTime": end.isoformat(),
                    "timeZone": "Europe/Paris",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 60 * 4},
                    ],
                },
            }
            event = service.events().insert(calendarId="primary", body=event).execute()
            print(f"Event created: {(event.get('htmlLink'))}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def parse_events(filename: str) -> list[list[datetime]]:
    with open(file=filename, encoding="utf-8", mode="r") as file:
        contents = file.readlines()

    events = []
    for line in contents:
        line = line.strip().split(" ")

        day, hours = line[1], line[2]
        day = reversed(day.split("/"))
        day = "-".join(day)

        [start_hour, end_hour] = hours.split("-")
        start = datetime.fromisoformat("T".join([day, start_hour]))
        end = datetime.fromisoformat("T".join([day, end_hour]))
        events.append([start, end])
    return events


if __name__ == "__main__":
    main()
