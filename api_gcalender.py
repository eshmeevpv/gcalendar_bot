from __future__ import print_function
import warnings
warnings.filterwarnings("ignore")
from google.oauth2 import service_account
from googleapiclient.discovery import build

#создаем скелет для работы с API Google календаря
class gcalender:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    file = 'calendar-407814-9dcde1ac902b.json'
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(filename=self.file, scopes=self.SCOPES)
        self.service = build('calendar', 'v3', credentials=credentials)

    def calenders_list(self):
        return self.service.calendarList().list().execute()

    def add_calender(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }
        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def add_event(self, calendar_id, body):
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()

    def show_events(self, calendar_id, max_start_time, min_end_time):
        return self.service.events().list(calendarId=calendar_id, timeMin=max_start_time, timeMax=min_end_time).execute()