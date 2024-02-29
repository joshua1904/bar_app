import flask
from flask import Flask, request, flash

import sql
import utils

DATABASE = "test.db"

app = Flask(__name__)
sql.init()
app.secret_key = "Test"




@app.route("/")
def index_page():
    settings = utils.get_settings_from_tuple(sql.get_settings())
    return flask.render_template("index.html", data=get_all_beer_states_2(settings.min_weight, settings.max_weight,
                                                                          settings.min_time_diff, settings.tolerance))


def set_serial_to_name(serial: str, name: str) -> bool:
    try:
        sql.set_serial_to_name(serial, name)
    except Exception:
        return False
    return True


@app.route("/edit")
def edit():
    settings = utils.get_settings_from_tuple(sql.get_settings())
    return flask.render_template("edit.html", min_weight=settings.min_weight, max_weight=settings.max_weight,
                                 min_time_diff=settings.min_time_diff, tolerance=settings.tolerance)


@app.route("/serialToName")
def get_serial_toName():
    try:
        serial_to_name_list = sql.get_serial_name_list()
    except Exception:
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
    settings = utils.get_settings_from_tuple(sql.get_settings())
    if set_serial_to_name(serial_number, name):
        flash(f"Successfully updated {serial_number}!", "info")
    else:
        flash(f"Could not update serial Number {serial_number}!")
    return flask.render_template("edit.html", min_weight=settings.min_weight, max_weight=settings.max_weight,
                                 min_time_diff=settings.min_time_diff, tolerance=settings.tolerance)


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form.get('delete_name')
    try:
        settings = utils.get_settings_from_tuple(sql.get_settings())
        sql.delete_serial_to_name(name)
    except:
        pass
    return flask.render_template("edit.html", min_weight=settings.min_weight, max_weight=settings.max_weight,
                                 min_time_diff=settings.min_time_diff, tolerance=settings.tolerance)


@app.route('/edit_settings', methods=['POST'])
def edit_settings():
    min_weight = request.form.get('min_weight')
    max_weight = request.form.get('max_weight')
    min_time_diff = request.form.get('min_time_diff')
    tolerance = request.form.get('tolerance')
    try:
        if min_weight >= max_weight:
            flash(f"Max weight has to be bigger than min Weight! min: {min_weight}, {max_weight}", "error")
           # sorry
            raise ValueError
        sql.update_settings(min_weight, max_weight, min_time_diff, tolerance)
        settings = utils.get_settings_from_tuple(sql.get_settings())
    except:
        settings = utils.get_settings_from_tuple(sql.get_settings())
    return flask.render_template("edit.html", min_weight=settings.min_weight, max_weight=settings.max_weight,
                                 min_time_diff=settings.min_time_diff, tolerance=settings.tolerance)


def get_all_beer_states_2(min_weight: int, max_weight: int, min_time_diff: int, tolerance: int):
    try:
        beer_states = sql.get_beer_states()
    except Exception:
        flask.jsonify([])
        return
    result = []
    for beer_state in beer_states:
        _, time_stamp, value, serial, last_seen, name = beer_state
        info = utils.get_info(min_time_diff, min_weight, max_weight, time_stamp, value, last_seen, tolerance, name, serial)
        result.append(info)
    return [{"beer_percentage": f"{info.percentage_of_beer}%", "color": info.info_color, "serial": info.serial,"name": info.name} for info in sorted(result, key=lambda x: x.percentage_of_beer)]


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
