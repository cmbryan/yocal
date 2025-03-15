from datetime import datetime
import os
import sqlite3

from flask import jsonify
from . import create_app


app = create_app()

db_path = 'db/YOCal.db'
assert os.path.exists(db_path), f"{db_path} not found"


@app.route("/test")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/")
def get_today():
    today_date = datetime.now()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Year_{today_date.year}"
                        " WHERE date = ?",
                        (today_date.strftime("%Y-%m-%d"),))
        result = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]
    
    if result:
        result_dict = dict(zip(column_names, result))
        return jsonify(result_dict)
    else:
        return jsonify({"error": f"No data found for {today_date.strftime('%Y-%m-%d')}"})


@app.route("/date/<int:year>/<int:month>/<int:day>")
def get_date(year, month, day):
    return f"<p>Year: {year}, Month: {month}, Day: {day}</p>"
