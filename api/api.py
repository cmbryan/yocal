from datetime import datetime
import os
import sqlite3
from typing import Dict

from flask import jsonify, request
from . import create_app


app = create_app()

yocal_path = 'db/YOCal.db'
assert os.path.exists(yocal_path), f"{yocal_path} not found"
yocal_master_path = 'db/YOCal_Master.db'
assert os.path.exists(yocal_master_path), f"{yocal_master_path} not found"


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

    data = _get_data(datetime(year, month, day))
    data["a_lections"] = _get_lections(data["a_code"])
    data["g_lections"] = _get_lections(data["g_code"])
    data["c_lections"] = _get_lections(data["c_code"])
    data["x_lections"] = _get_lections(data["x_code"])
    return jsonify(data)


def _get_lections(code: str) -> Dict:
    with sqlite3.connect(yocal_master_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM yocal_lections"
                       " WHERE code=?",
                       (code,))
        result = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

    return [dict(zip(column_names, row)) for row in result]


def _get_data(date: datetime.date) -> Dict:
    with sqlite3.connect(yocal_path) as conn:
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