import json
import os


def process_tr_file(cur_file: str, agg_team):
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


def process_ps_file(cur_file: str, agg_stats):
    if not os.path.exists(cur_file):
        return False
    with open(cur_file) as json_file:
        raw_data = json.load(json_file)

    for pid, p_data in raw_data.items():
        if pid in ["DEFENSE", "TEAM"]:
            continue
        if pid not in agg_stats:
            agg_stats[pid] = {}
        for stat in p_data:
            if stat not in agg_stats[pid]:
                agg_stats[pid][stat] = 0
            if stat == "Batter hits":
                hits = p_data[stat] - p_data.get("Batter hrs", 0)
                agg_stats[pid][stat] += hits
            else:
                agg_stats[pid][stat] += p_data[stat]


def sum_season_files(file_id: str):
    agg_stats = {}
    agg_team = {}
    failed = []
    tr_file_path = os.path.join('..', 'season_sim', 'results', f'{file_id}_season_sim_stats', 'team_records')
    ps_file_path = os.path.join('..', 'season_sim', 'results', f'{file_id}_season_sim_stats', 'player_stats')
    for day in range(0, 99):
        tr_filename = os.path.join(tr_file_path, f'day{day}.json')
        ps_filename = os.path.join(ps_file_path, f'day{day}.json')
        success = process_tr_file(tr_filename, agg_team)
        if not success:
            failed.append(str(day))
            continue
        process_ps_file(ps_filename, agg_stats)

    return {"output": agg_team, "failed": failed, "stats": agg_stats}
