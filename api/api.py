from copy import copy
from datetime import date, datetime
import os
from pydoc import text
import sqlite3
from typing import Dict

from click import File
from flask import jsonify, render_template, request
from jinja2 import Environment, FileSystemLoader
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
    return jsonify(_get_date(datetime.now()))


@app.route("/date")
def get_date():
    return jsonify(
        _get_date(
            date(
                request.args.get('year', type=int),
                request.args.get('month', type=int),
                request.args.get('day', type=int)
            )
        )
    )


@app.route("/test-display")
def get_test_display():
    date_obj = date(
        request.args.get('year', type=int),
        request.args.get('month', type=int),
        request.args.get('day', type=int)
    ) if request.args.get('year') \
    else datetime.now().date()
    
    data = _get_date(date_obj)

    if data.keys() == {"error"}:
        return jsonify(data), 404

    env = Environment(loader=FileSystemLoader('api/templates'))
    template = env.get_template('test_display.html')
    template.globals.update({"embolden_liturgy_lects": lambda x, y: f"<b>{x}</b>" if x in y else x})

    return template.render(data=data)


def _get_date(date_obj: datetime.date) -> Dict:
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
        "primary": [],
    }
    g_data = copy(a_data)
    c_data = copy(a_data)
    x_data = copy(a_data)

    if a_code:
        a_data = _get_lections(a_code)
        a_data["primary"] = []

    if g_code:
        g_data = _get_lections(g_code)
        g_data["primary"] = []

    if data["x_code"]:
        x_data = _get_lections(data["x_code"])
        x_data["primary"] = []

    if data["c_code"]:
        c_data = _get_lections(data["c_code"])
        c_data["primary"] = []

    # Commemorations
    if data["c_code"]:
        # Primary lect 1
        if data["is_comm_apos"]:
            c_data["primary"].append("lect_1")
        elif a_code:
            a_data["primary"].append("lect_1")

        # Primary lect 2
        if data["is_comm_gosp"]:
            c_data["primary"].append("lect_2")
        elif a_code and a_data["lect_2"]:
            a_data["primary"].append("lect_2")
        elif g_code and g_data["lect_2"]:
            g_data["primary"].append("lect_2")

    # Non-commemoration
    else:
        a_data["primary"].append("lect_1")
        if a_data["lect_2"]:
            a_data["primary"].append("lect_2")
        elif g_data["lect_2"]:
            g_data["primary"].append("lect_2")

    # As there is no Liturgy Mon-Fri in Lent, or on Holy Saturday, or on Wed and Fri of Cheesefare Week, remove the bold tags from the lections
    if a_code[0] == "G" \
            and (a_code[2] != "S" or a_code in ["G7Sat", "E36Wed", "E36Fri"]):
        for section in [a_data, g_data, c_data, x_data]:
            section["primary"] = []

    result["lections"] = {}
    result["lections"]["basic"] = []
    result["lections"]["commem"] = []
    result["lections"]["liturgy"] = []
    result["texts"] = []

    for idx in range(1, 3):
        lect_idx = f"lect_{idx}"
        text_idx = f"text_{idx}"

        for data in [a_data, g_data]:
            if data[lect_idx]:
                result["lections"]["basic"].append(data[lect_idx])
                result["texts"].append(data[text_idx])
                if lect_idx in data["primary"]:
                    result["lections"]["liturgy"].append(data[lect_idx])

        for data in [c_data, x_data]:
            if data[lect_idx]:
                result["lections"]["commem"].append(data[lect_idx])
                result["texts"].append(data[text_idx])
                if lect_idx in data["primary"]:
                    result["lections"]["liturgy"].append(data[lect_idx])

    return result


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