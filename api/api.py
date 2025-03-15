from datetime import datetime
import os
import sqlite3
from typing import Dict

from flask import jsonify, request
from . import create_app


app = create_app()

db_path = 'db/YOCal.db'
assert os.path.exists(db_path), f"{db_path} not found"


@app.route("/test")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/")
def get_today():
    return jsonify(_get_data(datetime.now()))


@app.route("/date")
def get_date():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)

    return jsonify(_get_data(datetime(year, month, day)))


def _get_data(date: datetime.date) -> Dict:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Year_{date.year}"
                        " WHERE date = ?",
                        (date.strftime("%Y-%m-%d"),))
        result = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]
    
    if result:
        return dict(zip(column_names, result))
    else:
        return {"error": f"No data found for {date.strftime('%Y-%m-%d')}"}