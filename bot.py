from api_gcalender import gcalender
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import io
import schedule
import time
from datetime import datetime, timedelta
from dateutil import tz
import re

#создали календарь (то есть добавили к нашему сервису новый календарь (изначально сервис пуст)
obj = gcalender()
calendar='27231f2ccb72dd31d6d6aa007bff8a1df0998687345d47cd1d8e60a651e8e38a@group.calendar.google.com'
#obj.add_calender(calendar_id=calendar)

#создали скелет формирования ивента для гугл календаря
def event_form(summary, description, start, end):
    return {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start,
            'timeZone': 'Europe/Moscow'
        },
        'end': {
            'dateTime': end,
            'timeZone': 'Europe/Moscow'
        },
        # 'attendees': attendees
    }

def show_statistics_chart(array, nickname, start_date, end_date):
    plt.hist(array, bins='auto')

    plt.xticks(rotation=90)
    plt.xlabel('Дата')
    plt.ylabel('Количество встреч')
    plt.title(f'Количество встреч с участием {nickname} по датам\nв промежутке от {start_date} до {end_date}')

    plt.gcf().set_size_inches(10, 10)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plt.clf()

    return buffer



# obj.add_event(calendar_id=calendar, body=event) - можете создать собстенное собрание по формату def event и убедится, что все работает корректно

import telebot

bot = telebot.TeleBot('6511790700:AAFAL_X9E1W4RJ9AhiseMMopM-Ec-betSOM')

members = dict()


# Функция получения информации о встречах на завтрашний день
def send_next_day_events():
    now = datetime.now()

    tomorrow = now + timedelta(days=1)
    start_tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, tzinfo=tz.tzlocal())
    rfc3339_start_tomorrow = start_tomorrow.replace(microsecond=0).isoformat()

    day_after_tomorrow = now + timedelta(days=2)
    start_day_after_tomorrow = datetime(day_after_tomorrow.year, day_after_tomorrow.month, day_after_tomorrow.day, 0, 0,
                                        0, tzinfo=tz.tzlocal())
    rfc3339_start_day_after_tomorrow = start_day_after_tomorrow.replace(microsecond=0).isoformat()

    events_for_tomorrow = obj.show_events(calendar_id=calendar, max_start_time=rfc3339_start_tomorrow, min_end_time=rfc3339_start_day_after_tomorrow)["items"]
    information = []
    for event in events_for_tomorrow:
        info = ""
        info += "Название: " + event['summary'] + "\n"
        info += "Описание: " + event['description'].split('Участники')[0][:-1]
        info += "Время начала: " + event['start']['dateTime'][11:16] + "\n"
        info += "Время окончания: " + event['end']['dateTime'][11:16] + "\n"
        participants = re.findall(r'[\w\.-]+@[\w\.-]+', event['description'])
        users = [nickname for nickname, email in members.items() if email in participants]
        info += "Участники: @" + ", @".join(users)
        information.append(info)

    return information

# schedule.every().day.at("18:00").do(send_next_day_events)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)


# --------------------------------------------------------------------------------------------------------------------
# Команда приветствия
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Это бот для составления и организации вашего расписания.\n\nПожалуйста, "
                                      "для начала зарегистрируйтесь с помощью команды /registration, иначе вы не сможете использовать весь функционал.\n\n"
                                      "Для получения большей информации о возможностях бота воспользуйтесь /help")


# --------------------------------------------------------------------------------------------------------------------
# Команда для отображения списка команд
@bot.message_handler(commands=['help'])
def help_message(message):
    commands = "Вы можете использовать следующие команды:\n\n" \
               "/help - вызывает эту же команду\n" \
               "/start - приветственное сообщение\n" \
               "/registration - зарегистрироваться (обязательно сделайте это, если еще не успели!)\n" \
               "/new_meeting - создание нового собрания\n" \
               "/statistics - статистика по всем встречам\n" \
               "/tomorrow_events - встречи в течение завтрашнего дня"
    bot.send_message(message.chat.id, commands)

# --------------------------------------------------------------------------------------------------------------------
# Отправка событий на завтрашний день
@bot.message_handler(commands=['tomorrow_events'])
def send_events(message):
    try:
        events_for_tomorrow = send_next_day_events()
        bot.send_message(message.chat.id, "Встречи на завтрашний день:" + "\n\n" + "\n\n".join(events_for_tomorrow))
    except:
        bot.send_message(message.chat.id, "Упс, что-то пошло не так...")


# --------------------------------------------------------------------------------------------------------------------
# Регистрация участников для получения их электронных почт
@bot.message_handler(commands=['registration'])
def registration(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите ваш адрес электронной почты в формате: example@gmail.com")
    bot.register_next_step_handler(message, process_email_step)

def process_email_step(message):
    email = message.text
    user_id = message.from_user.username
    if user_id in members.keys():
        bot.send_message(message.chat.id, "Вы уже были зарегистрированы ранее!")
    else:
        members[user_id] = email
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы!")
    print(members)


# --------------------------------------------------------------------------------------------------------------------
# Общая статистика по всем встречам за определенный срок
@bot.message_handler(commands=['statistics'])
def startt(message):
    bot.send_message(message.chat.id, "Введите дату начала промежутка, за который вы хотели бы узнать статистику по встречам в формате год-месяц-день:")
    bot.register_next_step_handler(message, stat_end_dates)

def stat_end_dates(message):
    global stat_starts
    stat_starts = message.text + "T00:00:00Z"
    bot.send_message(message.chat.id, "Введите дату конца промежутка в формате год-месяц-день:")
    bot.register_next_step_handler(message, showing_stats)

def showing_stats(message):
    stat_end = message.text + "T00:00:00Z"
    try:
        meetings_amount = len(obj.show_events(calendar_id=calendar, max_start_time=stat_starts, min_end_time=stat_end)["items"])
        answer = f"Количество встреч за указанный промежуток: {meetings_amount}"
    except:
        answer = "Упс, что-то пошло не так..."
    bot.send_message(message.chat.id, answer)


# --------------------------------------------------------------------------------------------------------------------
# Добавление нового события
@bot.message_handler(commands=['new_meeting'])
def start(message):
    bot.send_message(message.chat.id, "Введите название собрания:")
    bot.register_next_step_handler(message, start_date)

def start_date(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, "Введите дату начала собрания в формате год-месяц-день:")
    bot.register_next_step_handler(message, start_time)

def start_time(message):
    global start
    start = message.text
    bot.send_message(message.chat.id, "Введите время начала собрания в формате часы:минуты :")
    bot.register_next_step_handler(message, end_date)

def end_date(message):
    global stime
    stime = message.text
    bot.send_message(message.chat.id, "Введите дату конца собрания:")
    bot.register_next_step_handler(message, end_time)

def end_time(message):
    global end
    end = message.text
    bot.send_message(message.chat.id, "Введите время конца собрания в формате часы:минуты :")
    bot.register_next_step_handler(message, some_description)

def some_description(message):
    global etime
    etime = message.text
    bot.send_message(message.chat.id, "Введите описание собрания - что бы вы хотели на нем обсудить/сделать:")
    bot.register_next_step_handler(message, list_of_attendees)

def list_of_attendees(message):
    global description
    description = message.text
    bot.send_message(message.chat.id, "Введите через пробел список никнеймов участников, которых вы хотите пригласить на собрание:")
    bot.register_next_step_handler(message, adding_meeting)

def adding_meeting(message):
    usernames = message.text.split()
    attendees = []
    for username in usernames:
        try:
            attendees.append(members[username[1:]])
        except:
            bot.send_message(message.chat.id, f"Пользователь {username} не был зарегестрирован!")

    body = event_form(name, description + "\nУчастники:\n" + "\n".join(attendees), (start + "T" + stime + ":00"), (end + "T" + etime + ":00"))
    print(body)
    try:
        obj.add_event(calendar_id=calendar, body=body)
        answer = "Собрание успешно добавлено!"
    except:
        answer = "Возникла ошибка!"
    bot.send_message(message.chat.id, answer)

# --------------------------------------------------------------------------------------------------------------------
# Личная статистика по всем встречам за определенный срок
@bot.message_handler(commands=['my_statistics'])
def registr(message):
    bot.send_message(message.chat.id, "Введите дату начала промежутка, за который вы хотели бы узнать статистику по встречам, в которых вы принимали участие, в формате год-месяц-день:")
    bot.register_next_step_handler(message, stat_end_date)

def stat_end_date(message):
    global stat_start
    stat_start = message.text + "T00:00:00Z"
    bot.send_message(message.chat.id, "Введите дату конца промежутка в формате год-месяц-день:")
    bot.register_next_step_handler(message, showing_stat)

def showing_stat(message):
    stat_end = message.text + "T00:00:00Z"
    user_id = message.from_user.username
    mail = members[user_id]
    try:
        events = obj.show_events(calendar_id=calendar, max_start_time=stat_start, min_end_time=stat_end)["items"]
        meetings = []
        for event in events:
            if mail in event['description']:
                meetings.append(event['start']['dateTime'])
        print(meetings)
        meetings = np.array(meetings)
        meetings_dates = np.array([np.datetime64(meeting) for meeting in meetings])
        graph_buffer = show_statistics_chart(meetings_dates, user_id, stat_start[:-10], stat_end[:-10])
        bot.send_message(message.chat.id, f'За промежуток от {stat_start[:-10]} до {stat_end[:-10]} {user_id} поучаствовал в {len(events)} встречах')
        bot.send_message(message.chat.id, 'Вот их распределение по дням:')
        bot.send_photo(message.chat.id, graph_buffer)
    except:
        answer = "Упс, что-то пошло не так..."
        bot.send_message(message.chat.id, answer)

bot.polling()