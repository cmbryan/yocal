from copy import copy
from datetime import date, datetime
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
    date_obj = date(year, month, day)

    data = _get_data(date_obj)
    
    if not data:
        return {"error": f"No data found for {date_obj.strftime('%Y-%m-%d')}"}

    # Construct the dict matching our API
    desig_a = data["desig_a"]
    desig_g = data["desig_g"]
    desig = ", ".join([desig_a, desig_g]) if desig_a and desig_g \
        else desig_a if desig_a else None

    result = {
        "day_name": data["day_name"],
        "day_ord": data["ord"],
        "month": data["month"],
        "year": data["year"],
        "fast": data["fast"],
        "tone": data["tone"],
        "eothinon": data["eothinon"],
        "basil": data["basil"],  # TODO replace with enum for Basil, Chrysostom, on None
        "desig": desig,
        "commem": data["major_commem"],
        "fore_after": data["fore_after"],
        "global_saints": data["class_5"],
        "british_saints": data["british"],
    }

    a_code = data["a_code"]
    g_code = data["g_code"] if data["g_code"] != a_code else None

    a_data = {
        "lect_1": None,
        "text_1": None,
        "lect_2": None,
        "text_2": None,
        "primary": None,
    }
    g_data = copy(a_data)
    c_data = copy(a_data)
    x_data = copy(a_data)

    if a_code:
        a_data = _get_lections(a_code)
        a_data["primary"] = None

    if g_code:
        g_data = _get_lections(g_code)
        g_data["primary"] = None

    if data["x_code"]:
        x_data = _get_lections(data["x_code"])
        x_data["primary"] = None

    if data["c_code"]:
        c_data = _get_lections(data["c_code"])
        c_data["primary"] = None

    # Commemorations
    if data["c_code"]:
        # Primary lect 1
        if data["is_comm_apos"]:
            c_data["primary"] = "lect_1"
        elif a_code:
            a_data["primary"] = "lect_1"

        # Primary lect 2
        if data["is_comm_gosp"]:
            c_data["primary"] = "lect_2"
        elif a_code and a_data["lect_2"]:
            a_data["primary"] = "lect_2"
        elif g_code and g_data["lect_2"]:
            g_data["primary"] = "lect_2"

    # Non-commemoration
    else:
        a_data["primary"] = "lect_1"
        if a_data["lect_2"]:
            a_data["primary"] = "lect_2"
        elif g_data["lect_2"]:
            g_data["primary"] = "lect_2"

    result["lections"] = {
        "a": a_data,
        "g": g_data,
        "x": x_data,
        "c": c_data,
    }

    # As there is no Liturgy Mon-Fri in Lent, or on Holy Saturday, or on Wed and Fri of Cheesefare Week, remove the bold tags from the lections
    if a_code[0] == "G" and a_code[2] == "G":
        for section in result["lections"].values():
            section["primary"] = None


    return jsonify(result)


def _get_lections(code: str) -> Dict:
    with sqlite3.connect(yocal_master_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM yocal_lections"
                       " WHERE code=?",
                       (code,))
        result = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]

    return dict(zip(column_names, result))


def _get_data(date_obj: datetime.date) -> Dict:
    with sqlite3.connect(yocal_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Year_{date_obj.year}"
                        " WHERE date = ?",
                        (date_obj.strftime("%Y-%m-%d"),))
        result = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]

    if result:
        return dict(zip(column_names, result))
    else:
        return None