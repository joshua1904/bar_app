import dataclasses
import sqlite3
import flask
from flask import Flask, request, flash

import sql
import utils
from waitress import serve
import os
DATABASE = "test.db"

app = Flask(__name__)
sql.init()
app.config["UPLOAD_FOLDER"] = os.path.join("static", "IMG")
edit_symbol = os.path.join(app.config["UPLOAD_FOLDER"], "edit_symbol.png")


@app.route("/")
def index_page():
    settings = utils.get_settings_from_tuple(sql.get_settings())
    return flask.render_template("index.html", edit_symbol=edit_symbol, data=get_all_beer_states_2(settings.min_weight, settings.max_weight,
                                                                          settings.min_time_diff, settings.tolerance))


def set_serial_to_name(serial: str, name: str) -> bool:
    try:
        sql.set_serial_to_name(serial, name)
    except sqlite3.Error:
        return False
    return True


@app.route("/edit")
def edit():
    return _return_edit_html()


@app.route("/serialToName")
def get_serial_toName():
    try:
        serial_to_name_list = sql.get_serial_name_list()
    except sqlite3.Error:
        return flask.jsonify([])
    result = {}
    for i in serial_to_name_list:
        _, serial, name = i
        result[serial] = name
    return flask.jsonify(result)


@app.route('/update', methods=['POST'])
def update():
    serial_number = request.form.get('serial_number')
    name = request.form.get('name')
    if set_serial_to_name(serial_number, name):
        flash(f"Successfully updated {serial_number}!", "info")
    else:
        flash(f"Could not update serial Number {serial_number}!")
    return _return_edit_html()


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form.get('delete_name')
    try:
        sql.delete_serial_to_name(name)
    except:
        pass
    return _return_edit_html()


@app.route('/edit_settings', methods=['POST'])
def edit_settings():
    min_weight = int(request.form.get('min_weight'))
    max_weight = int(request.form.get('max_weight'))
    min_time_diff = request.form.get('min_time_diff')
    tolerance = request.form.get('tolerance')
    try:
        if min_weight <= max_weight:
            sql.update_settings(min_weight, max_weight, min_time_diff, tolerance)
        else:
            flash(f"Max weight has to be bigger than min Weight! min: {min_weight}, {max_weight}", "error")
    except sqlite3.Error:
        flash("Sql Error", "error")
    return _return_edit_html()


def get_all_beer_states_2(min_weight: int, max_weight: int, min_time_diff: int, tolerance: int):
    try:
        beer_states = sql.get_beer_states()
        empty_filter, full_filter, not_used_filter, offline_filter = sql.get_filter()
    except sqlite3.Error:
        flash("Sql Error", "error")
        return []

    result = []
    for beer_state in beer_states:
        _, time_stamp, value, serial, last_seen, name = beer_state
        info = utils.get_info(min_time_diff, min_weight, max_weight, time_stamp, value, last_seen, tolerance, name,
                              serial)
        if is_selected(empty_filter, full_filter, not_used_filter, offline_filter, info.info_color):
            result.append(info)
    return [dataclasses.asdict(info) for info in sorted(result, key=lambda x: x.percentage_of_beer)]


def is_selected(empty_filter: bool, full_filter: bool, not_used_filter: bool, offline_filter: bool, current_color: str):
    if current_color == "red" and not empty_filter:
        return False
    if current_color == "green" and not full_filter:
        return False
    if current_color == "grey" and not not_used_filter:
        return False
    if current_color == "black" and not offline_filter:
        return False
    return True


@app.route('/set_filter', methods=['POST'])
def set_filter():
    empty = request.form.get("empty_checkbox") is not None
    full = request.form.get("full_checkbox") is not None
    not_used = request.form.get("not_used_checkbox") is not None
    offline = request.form.get("offline_checkbox") is not None
    try:
        sql.update_filter(empty, full, not_used, offline)
    except sqlite3.Error:
        flash("Sql Error", "error")
    return _return_edit_html()


def _return_edit_html():
    settings = utils.get_settings_from_tuple(sql.get_settings())
    empty, full, not_used, offline = sql.get_filter()
    return flask.render_template("edit.html", min_weight=settings.min_weight, max_weight=settings.max_weight,
                                 min_time_diff=settings.min_time_diff, tolerance=settings.tolerance, empty=empty,
                                 offline=offline, not_used=not_used, full=full, edit_symbol=edit_symbol)


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
