from datetime import datetime, timedelta
from pydoc import describe
import sqlite3
from flask import Blueprint, render_template, redirect, url_for
import os
from .forms import AppointmentForm

bp = Blueprint("main", __name__, url_prefix="/")
DB_FILE = os.environ.get("DB_FILE")


@bp.route("/", methods=["GET", "POST"])
def main():
    # return redirect(f'/{new_year}/{new_month}/{new_day}')
    # return render_template("main.html", rows=rows, form=form)
    d = datetime.now()
    return redirect(url_for(".daily", year=d.year, month=d.month, day=d.day))


@bp.route("/<int:year>/<int:month>/<int:day>", methods=["GET", "POST"])
def daily(year, month, day):
    rows = []
    form = AppointmentForm()
    if form.validate_on_submit():
        print("HELLO")
        with sqlite3.connect(DB_FILE) as conn:
            params = {
                'name': form.name.data,
                'start_date': form.start_date.data,
                'start_time': form.start_time.data,
                'end_date': form.end_date.data,
                'end_time': form.end_time.data,
                'description': form.description.data,
                'private': form.private.data
            }
            start_datetime_string = str(
                params["start_date"]) + " " + str(params["start_time"])
            end_datetime_string = str(
                params["end_date"]) + " " + str(params["end_time"])
            new_params = {
                'name': form.name.data,
                'start_date': start_datetime_string,
                'end_date': end_datetime_string,
                'description': form.description.data,
                'private': form.private.data
            }
            print(tuple(str(params['start_date'])))
            year = tuple(str(params['start_date']))
            x = slice(0, 4)
            new_year = int("".join(year[x]))
            print(new_year)
            month = tuple(str(params['start_date']))
            x = slice(5, 7)
            new_month = int("".join(month[x]))
            print(new_month)
            day = tuple(str(params['start_date']))
            x = slice(8, 10)
            new_day = int("".join(day[x]))
            print(new_day)
            curs = conn.cursor()
            curs.execute("""
                INSERT INTO appointments(name, start_datetime, end_datetime, description, private)
                VALUES (:name, :start_date, :end_date, :description, :private)
            """, new_params)
            # curs.execute("""
            # INSERT INTO appointments(name,start_datetime, end_datetime, description, private)
            # VALUES
            # (params['name'], start_datetime_string, end_datetime_string, new_description, new_private)
            # """)
        return redirect(f'/{new_year}/{new_month}/{new_day}')
    date_time_obj = datetime(year, month, day)
    next_day = day + 1
    next_day_obj = datetime(year, month, next_day)
    with sqlite3.connect(DB_FILE) as conn:
        curs = conn.cursor()
        curs.execute("""
        SELECT id, name, start_datetime, end_datetime
        FROM appointments
        WHERE start_datetime BETWEEN :date_time_obj AND :next_day_obj
        ORDER BY start_datetime
        """, {"date_time_obj": date_time_obj, "next_day_obj": next_day_obj})
        values = curs.fetchall()
        for x in values:
            start_time = datetime.strptime(
                x[2], '%Y-%m-%d %H:%M:%S').strftime("%H:%M")
            end_time = datetime.strptime(
                x[3], '%Y-%m-%d %H:%M:%S').strftime("%H:%M")
            rows.append(tuple([x[1], start_time, end_time]))
    return render_template("main.html", rows=rows, form=form)
