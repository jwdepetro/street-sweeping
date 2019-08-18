import calendar
import datetime
import os

from dateutil.tz import tzlocal
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from ics import Calendar, Event
from wtforms import SelectField, SubmitField, TimeField
from wtforms import SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput

load_dotenv()


class AppConfig:
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV')


def make_app():
    app = Flask(__name__)
    app.template_folder = '.'
    app.config.from_object(AppConfig)
    return app


app = make_app()


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
        self.weekday = int(weekday)
        self.interval = [int(i) for i in interval]
        self.start_time = start_time
        self.end_time = end_time
        self.year = datetime.datetime.now().year
        self.month = datetime.datetime.now().month
        self.tz = tzlocal()
        self.cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        self.ical = Calendar()

    def get_date(self, interval) -> datetime.datetime:
        month_cal = self.cal.monthdatescalendar(self.year, self.month)
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
                self.month = self.month + 1
            my_file.writelines(self.ical)
            my_file.close()
        return my_file


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class CalenderForm(FlaskForm):
    interval_choices = [(str(v), 'Every {} weeks'.format(v + 1)) for v in range(4)]
    weekday_choices = [
        (str(calendar.SUNDAY), 'Sunday'),
        (str(calendar.MONDAY), 'Monday'),
        (str(calendar.TUESDAY), 'Tuesday'),
        (str(calendar.WEDNESDAY), 'Wednesday'),
        (str(calendar.THURSDAY), 'Thursday'),
        (str(calendar.FRIDAY), 'Friday'),
        (str(calendar.SATURDAY), 'Saturday')
    ]
    interval = MultiCheckboxField('Interval', [DataRequired()], choices=interval_choices)
    weekday = SelectField('Day of week', validators=[DataRequired()], choices=weekday_choices)
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Create')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = CalenderForm()
    if request.method == 'POST' and form.validate():
        cal = StreetSweepingCalendar(
            weekday=form.weekday.data,
            interval=form.interval.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        cal.make_file()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run()
