import calendar
import datetime

from dateutil.tz import tzlocal
from ics import Calendar, Event

ical = Calendar()
cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
y = datetime.datetime.now().year
m = datetime.datetime.now().month
tz = tzlocal()

# first and third tuesday of every month
DAY_OF_WEEK = calendar.TUESDAY
INTERVAL = (1, 3)


def get_date(month, interval) -> datetime.datetime:
    month_cal = cal.monthdatescalendar(y, month)
    date = [d for week in month_cal for d in week if d.weekday() == DAY_OF_WEEK and d.month == month][interval - 1]
    time = datetime.time(8, 0, 0)
    return datetime.datetime.combine(date, time, tz)


def create_event(date) -> Event:
    e = Event()
    e.name = "Street Sweeping"
    e.begin = date
    return e


with open('my.ics', 'w') as my_file:
    while m < 13:
        for i in INTERVAL:
            date = get_date(m, i)
            event = create_event(date)
            ical.events.add(event)
            print(date.isoformat())
        m = m + 1
    my_file.writelines(ical)
