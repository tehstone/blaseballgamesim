import json
import os

import numpy as np


def process_file(cur_file: str, agg_team):

    print(cur_file)
    if not os.path.exists(cur_file):
        return False
    with open(cur_file) as json_file:
        raw_data = json.load(json_file)

    for team in raw_data:
        if team not in agg_team:
            agg_team[team] = {'wins': 0, 'losses': 0, 'days': []}
        cur_data = raw_data[team]
        agg_team[team]['wins'] += int(cur_data['wins'])
        agg_team[team]['losses'] += int(cur_data['losses'])
        agg_team[team]['days'] = agg_team[team]['days'] + cur_data['days']
    return True


def sum_season_files(file_id: str):
    agg_team = {}
    failed = []
    file_path = os.path.join('..', 'season_sim', 'results', f'{file_id}_season_sim_stats', 'team_records')
    for day in range(0, 99):
        filename = os.path.join(file_path, f'day{day}.json')
        success = process_file(filename, agg_team)
        if not success:
            failed.append(str(day))

    return {"output": agg_team, "failed": failed}
