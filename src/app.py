import os
import logging
from logging import Formatter, FileHandler
from flask import Flask, request, render_template

from power_rankings import run_power_ranking_sim
from season_sim import run_season_sim
from season_sim_sums import sum_season_files

app = Flask(__name__)
from daily_sim import run_daily_sim

_VERSION = 1  # API version


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/v{}/powerrankings'.format(_VERSION), methods=["GET"])
def powerrankings():
    iterations = int(request.get_json()['iterations'])
    season = int(request.get_json()['season'])

    return run_power_ranking_sim(season, iterations)


@app.route('/v{}/seasonsim'.format(_VERSION), methods=["GET"])
def seasonsim():
    iterations = request.get_json()['iterations']
    season = request.get_json()['season']
    day = request.get_json()['day']
    file_id = request.get_json()['file_id']
    try:
        seg_size = request.get_json()['seg_size']
    except KeyError:
        seg_size = None

    return run_season_sim(int(season), int(day), file_id, int(iterations), int(seg_size), True)

@app.route('/v{}/sumseason'.format(_VERSION), methods=["GET"])
def sumseason():
    file_id = request.get_json()['file_id']

    return sum_season_files(file_id)

@app.route('/v{}/dailysim'.format(_VERSION), methods=["GET"])
def dailysim():
    iterations = request.get_json()['iterations']
    try:
        day = request.get_json()['day']
    except KeyError:
        day = None
    try:
        home_team = request.get_json()['home_team']
    except KeyError:
        home_team = None
    try:
        away_team = request.get_json()['away_team']
    except KeyError:
        away_team = None
    try:
        save_stlats_str = request.get_json()['save_stlats']
        save_stlats = True
        if save_stlats_str == "false":
            save_stlats = False
    except KeyError:
        save_stlats = True

    return run_daily_sim(iterations, day, home_team, away_team, save_stlats)


@app.errorhandler(500)
def internal_error(error):
    print("*** 500 ***\n{}".format(str(error)))  # ghetto logging


@app.errorhandler(404)
def not_found_error(error):
    print("*** 404 ***\n{}".format(str(error)))

if not app.debug:
    file_handler = FileHandler('error.log')
    o_file_handler = FileHandler('gunicorn')
    o_file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: \
            %(message)s [in %(pathname)s:%(lineno)d]')
    )
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: \
            %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    o_file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(o_file_handler)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    print("Started app.py on port: {port}")
    app.run(host='0.0.0.0', port=port)
