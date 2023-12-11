from __future__ import print_function
from google.oauth2 import service_account
from googleapiclient.discovery import build

from telepot.loop import MessageLoop
import telepot

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

#создали календарь (то есть добавили к нашему сервису новый календарь (изначально сервис пуст)
obj = gcalender()
calendar='27231f2ccb72dd31d6d6aa007bff8a1df0998687345d47cd1d8e60a651e8e38a@group.calendar.google.com'
#obj.add_calender(calendar_id=calendar)

#создали скелет формирования ивента для гугл календаря
def event_form(summary, start, end):
    return {
      'summary': summary,
      'start': {
        'date': start,
      },
      'end': {
        'date': end
      }
    }

# obj.add_event(calendar_id=calendar, body=event) - можете создать собстенное собрание по формату def event и убедится, что все работает корректно

#создаем самого телеграм бота
bot = telepot.Bot('6511790700:AAFAL_X9E1W4RJ9AhiseMMopM-Ec-betSOM')
bot.sendMessage(330542731, "Введите информацию о собрании в следующем порядке:\n Название собрания")

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    text = msg["text"]
    try:
        obj.add_event(calendar_id=calendar, body=event_form(text, '2023-12-07', '2023-12-08'))
        answer = 'Собрание успешно добавлено'
    except:
        answer = "Неправильный формат ввода"
    bot.sendMessage(chat_id, "answer: {}".format(answer))


MessageLoop(bot, handle).run_as_thread()

while True:
    n = input('To stop enter "stop":')
    if n.strip() == 'stop':
        break