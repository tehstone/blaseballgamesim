from typing import Any, Dict
import os
import json
import time
from joblib import load

from src.common import get_player_stlats
from src.common import BlaseballStatistics as Stats, blood_name_map
from src.common import ForbiddenKnowledge as FK
from src.common import BloodType, Team, team_id_map, blood_id_map, fk_key, Weather
from src.team_state import TeamState, DEF_ID
from src.game_state import GameState, InningHalf

lineups_by_team: Dict[str, Dict[int, str]] = {}
stlats_by_team: Dict[str, Dict[str, Dict[FK, float]]] = {}
game_stats_by_team: Dict[str, Dict[str, Dict[Stats, float]]] = {}
names_by_team: Dict[str, Dict[str, str]] = {}
blood_by_team: Dict[str, Dict[str, BloodType]] = {}
team_states: Dict[Team, TeamState] = {}
starting_pitchers: Dict[str, str] = {}

def setup(season: int, day: int):
    try:
        with open(os.path.join('season_sim', 'stlats', f"s{season}_d{day}_stlats.json"), 'r', encoding='utf8') as json_file:
            player_stlats_list = json.load(json_file)
    except FileNotFoundError:
        player_stlats_list = get_player_stlats(season, day)
    for player in player_stlats_list:
        team_id = player["team_id"]
        player_id = player["player_id"]
        pos = int(player["position_id"]) + 1
        if "position_type_id" in player:
            if player["position_type_id"] == "0":
                if team_id not in lineups_by_team:
                    lineups_by_team[team_id] = {}
                lineups_by_team[team_id][pos] = player_id
            else:
                if team_id not in starting_pitchers:
                    starting_pitchers[team_id] = player_id
        else:
            if player["position_type"] == "BATTER":
                if team_id not in lineups_by_team:
                    lineups_by_team[team_id] = {}
                lineups_by_team[team_id][pos] = player_id
            else:
                if team_id not in starting_pitchers:
                    starting_pitchers[team_id] = player_id

        if team_id not in stlats_by_team:
            stlats_by_team[team_id] = {}
        stlats_by_team[team_id][player_id] = get_stlat_dict(player)

        if team_id not in game_stats_by_team:
            game_stats_by_team[team_id] = {}
            game_stats_by_team[team_id][DEF_ID] = {}
        game_stats_by_team[team_id][player_id] = {}

        if team_id not in names_by_team:
            names_by_team[team_id] = {}
        names_by_team[team_id][player_id] = player["player_name"]

        if team_id not in blood_by_team:
            blood_by_team[team_id] = {}
        try:
            blood_by_team[team_id][player_id] = blood_id_map[int(player["blood"])]
        except ValueError:
            blood_by_team[team_id][player_id] = blood_name_map[player["blood"]]


def get_stlat_dict(player: Dict[str, Any]) -> Dict[FK, float]:
    ret_val: Dict[FK, float] = {}
    for k in fk_key:
        str_name = fk_key[k]
        ret_val[k] = float(player[str_name])
    return ret_val

def print_info():
    for team in names_by_team.keys():
        print(str(team_id_map[team]) + ":")
        for k in names_by_team[team]:
            print("\t"+names_by_team[team][k])
        print()

def make_team_states(season: int, day: int):
    for team in names_by_team.keys():
        if team in team_id_map:
            team_states[team_id_map[team]] = TeamState(
                team_id=team,
                season=season,
                day=day,
                num_bases=4,
                balls_for_walk=4,
                strikes_for_out=3,
                outs_for_inning=3,
                lineup=lineups_by_team[team],
                rotation={1: "starting_pitcher"},
                starting_pitcher=starting_pitchers[team],
                stlats=stlats_by_team[team],
                game_stats=game_stats_by_team[team],
                blood=blood_by_team[team],
                player_names=names_by_team[team],
                cur_batter_pos=1,
            )

season = 13
day = 0
setup(season, day)
#print_info()
make_team_states(season, day)
game = GameState(
    game_id="1",
    season=season,
    day=day,
    home_team=team_states[Team.DALE],
    away_team=team_states[Team.TIGERS],
    home_score=0,
    away_score=0,
    inning=1,
    half=InningHalf.TOP,
    outs=0,
    strikes=0,
    balls=0,
    weather=Weather.BIRDS,
)
model = load(os.path.join("..", "season_sim", "models", "pitch_v1.joblib"))
fv = game.gen_pitch_fv(
    game.cur_batting_team.get_cur_batter_feature_vector(),
    game.cur_pitching_team.get_pitcher_feature_vector(),
    game.cur_pitching_team.get_defense_feature_vector()
)
#print("fv = "+ str(fv))
#model.predict_proba()
t0 = time.time()
sim_run_count = 100.0
for x in range(int(sim_run_count)):
    game.simulate_game()
    game.reset_game_state()
t1 = time.time()
print(f'{t1-t0} timing')
home_pitcher = game.home_team.player_names[game.home_team.starting_pitcher]
home_so_total = game.home_team.game_stats[game.home_team.starting_pitcher][Stats.PITCHER_STRIKEOUTS]
home_sho_total = game.home_team.game_stats[game.home_team.starting_pitcher][Stats.PITCHER_SHUTOUTS]
home_so_avg = home_so_total / sim_run_count
home_sho_avg = home_sho_total / sim_run_count
away_pitcher = game.away_team.player_names[game.away_team.starting_pitcher]
away_so_total = game.away_team.game_stats[game.away_team.starting_pitcher][Stats.PITCHER_STRIKEOUTS]
away_sho_total = game.away_team.game_stats[game.away_team.starting_pitcher][Stats.PITCHER_SHUTOUTS]
away_so_avg = away_so_total / sim_run_count
away_sho_avg = away_sho_total / sim_run_count
home_wins = game.home_team.game_stats[DEF_ID][Stats.TEAM_WINS]
away_wins = game.away_team.game_stats[DEF_ID][Stats.TEAM_WINS]
home_win_per = home_wins / sim_run_count
away_win_per = away_wins / sim_run_count

print(f'{home_pitcher}:')
print(f'\tavg strikeouts: {home_so_avg}\ttotal strikeout: {home_so_total}')
print(f'\tavg shutouts: {home_sho_avg}\ttotal shutouts: {home_sho_total}')
print(f'{away_pitcher}:')
print(f'\tavg strikeouts: {away_so_avg}\ttotal strikeout: {away_so_total}')
print(f'\tavg shutouts: {away_sho_avg}\ttotal shutouts: {away_sho_total}')
print(f'home win %: {home_win_per}')
print(f'away win %: {away_win_per}')