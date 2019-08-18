import calendar
import datetime
import os

from dateutil.tz import tzlocal
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf import FlaskForm
from ics import Calendar, Event
from wtforms import SelectField, SubmitField, TimeField
from wtforms import SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput

load_dotenv()


# ical = Calendar()
# cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
# y = datetime.datetime.now().year
# m = datetime.datetime.now().month
# tz = tzlocal()
# start_time = datetime.time(9, 0, 0)
# end_time = datetime.time(12, 0, 0)

# first and third tuesday of every month
# DAY_OF_WEEK = calendar.TUESDAY
# INTERVAL = (1, 3)

class AppConfig:
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV')


class StreetSweepingCalendar:
    weekday = None
    interval = []
    start_time = None
    end_time = None
    year = None
    month = None
    tz = None
    cal = None
    ical = None

    def __init__(self, weekday, interval, start_time, end_time):
        self.weekday = weekday
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.year = datetime.datetime.now().year
        self.month = datetime.datetime.now().month
        self.tz = tzlocal()
        self.cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        self.ical = Calendar()

    def get_date(self, interval) -> datetime.datetime:
        month_cal = self.cal.monthdatescalendar(y, self.month)
        date = [d for week in month_cal for d in week
                if d.weekday() == self.weekday and d.month == self.month][interval]
        time = datetime.time(8, 0, 0)
        return datetime.datetime.combine(date, time, self.tz)

    def create_event(self, date) -> Event:
        e = Event()
        e.name = "Street Sweeping"
        e.begin = datetime.datetime.combine(date, self.start_time, self.tz)
        e.end = datetime.datetime.combine(date, self.end_time, self.tz)
        return e

    def make_file(self):
        with open('my.ics', 'w') as my_file:
            while self.month < 13:
                for i in self.interval:
                    date = self.get_date(i)
                    event = self.create_event(date)
                    self.ical.events.add(event)
                    print(date.isoformat())
                self.month = self.month + 1
            my_file.writelines(self.ical)
            my_file.close()
        return my_file


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class CalenderForm(FlaskForm):
    interval_choices = [(v, 'Every {} weeks'.format(v + 1)) for v in range(4)]
    weekday_choices = [
        (calendar.SUNDAY, 'Sunday'),
        (calendar.MONDAY, 'Monday'),
        (calendar.TUESDAY, 'Tuesday'),
        (calendar.WEDNESDAY, 'Wednesday'),
        (calendar.THURSDAY, 'Thursday'),
        (calendar.FRIDAY, 'Friday'),
        (calendar.SATURDAY, 'Saturday')
    ]
    # interval = SelectMultipleField('Interval', validators=[DataRequired()], choices=interval_choices)
    interval = MultiCheckboxField('Interval', [DataRequired()], choices=interval_choices)
    weekday = SelectField('Day of week', validators=[DataRequired()], choices=weekday_choices)
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Create')


def make_app():
    app = Flask(__name__)
    app.template_folder = '.'
    app.config.from_object(AppConfig)
    return app


app = make_app()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = CalenderForm()
    if form.validate_on_submit():
        cal = StreetSweepingCalendar(
            weekday=form.weekday,
            interval=form.interval,
            start_time=form.start_time,
            end_time=form.end_time
        )
        cal.make_file()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run()
