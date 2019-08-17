import calendar
import datetime

c = calendar.Calendar(firstweekday=calendar.SUNDAY)
y = datetime.datetime.now().year
m = datetime.datetime.now().month


def get_date(year, month, day, interval):
    month_cal = c.monthdatescalendar(year, month)
    return [d for week in month_cal for d in week if d.weekday() == day and d.month == month][interval - 1]


while m < 13:
    print(get_date(y, m, calendar.TUESDAY, 1))
    print(get_date(y, m, calendar.TUESDAY, 3))
    m = m + 1
