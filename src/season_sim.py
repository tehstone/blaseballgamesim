from os import path
from typing import Any, Dict
import os
import json

from src.common import get_stlats_for_season, blood_name_map
from src.common import BlaseballStatistics as Stats
from src.common import ForbiddenKnowledge as FK
from src.common import BloodType, Team, team_id_map, blood_id_map, fk_key, Weather, team_name_map
from src.team_state import TeamState, DEF_ID
from src.game_state import GameState, InningHalf

lineups_by_team: Dict[str, Dict[int, str]] = {}
stlats_by_team: Dict[str, Dict[str, Dict[FK, float]]] = {}
game_stats_by_team: Dict[str, Dict[str, Dict[Stats, float]]] = {}
names_by_team: Dict[str, Dict[str, str]] = {}
blood_by_team: Dict[str, Dict[str, BloodType]] = {}
team_states: Dict[Team, TeamState] = {}
rotations_by_team: Dict[str, Dict[int, str]] = {}

day_lineup = {}
day_stlats = {}
day_names = {}
day_blood = {}
day_rotations = {}

iterations = 10

def setup_season(season:int):
    with open(os.path.join('..', 'season_sim', 'season_data', f"season{season + 1}.json"), 'r', encoding='utf8') as json_file:
        raw_season_data = json.load(json_file)
        for game in raw_season_data:
            game_id = game["id"]
            day = int(game["day"])
            home_pitcher = game["homePitcher"]
            away_pitcher = game["awayPitcher"]
            home_team = game["homeTeam"]
            away_team = game["awayTeam"]
            home_team_name = game["homeTeamName"]
            away_team_name = game["awayTeamName"]
            weather = Weather(game["weather"])
            print(f'Day {day}, Weather {weather.name}: {away_team_name} at {home_team_name}')
            if day == 99:
                break
            update_team_states(season, day, home_team, home_pitcher, weather, True)
            home_team_state = team_states[team_id_map[home_team]]
            update_team_states(season, day, away_team, away_pitcher, weather, False)
            away_team_state = team_states[team_id_map[away_team]]
            game = GameState(
                game_id=game_id,
                season=season,
                day=day,
                home_team=home_team_state,
                away_team=away_team_state,
                home_score=0,
                away_score=0,
                inning=1,
                half=InningHalf.TOP,
                outs=0,
                strikes=0,
                balls=0,
                weather=weather
            )
            for x in range(0, iterations):
                game.simulate_game()
                game.reset_game_state()


def load_all_state(season: int):
    if not path.exists(os.path.join('..', 'season_sim', 'stlats', f"s{season}_d98_stlats.json")):
        get_stlats_for_season(season)

    for day in range(0, 99):
        reset_daily_cache()
        filename = os.path.join('..', 'season_sim', 'stlats', f"s{season}_d{day}_stlats.json")
        with open(filename, 'r', encoding='utf8') as json_file:
            player_stlats_list = json.load(json_file)
        for player in player_stlats_list:
            if day == 6 and player["team_id"] == "105bc3ff-1320-4e37-8ef0-8d595cb95dd0":
                x = 1
            team_id = player["team_id"]
            player_id = player["player_id"]
            pos = int(player["position_id"]) + 1
            if "position_type_id" in player:
                if player["position_type_id"] == "0":
                    if team_id not in lineups_by_team:
                        lineups_by_team[team_id] = {}
                    lineups_by_team[team_id][pos] = player_id
                else:
                    if team_id not in rotations_by_team:
                        rotations_by_team[team_id] = {}
                    rotations_by_team[team_id][pos] = player_id
            else:
                if player["position_type"] == "BATTER":
                    if team_id not in lineups_by_team:
                        lineups_by_team[team_id] = {}
                    lineups_by_team[team_id][pos] = player_id
                else:
                    if team_id not in rotations_by_team:
                        rotations_by_team[team_id] = {}
                    rotations_by_team[team_id][pos] = player_id
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
        if day > 0 and (len(lineups_by_team) != len(day_lineup[day - 1]) or (len(rotations_by_team) != len(day_rotations[day - 1]))):
            day_lineup[day] = day_lineup[day-1]
            day_stlats[day] = day_stlats[day-1]
            day_names[day] = day_names[day-1]
            day_blood[day] = day_blood[day-1]
            day_rotations[day] = day_rotations[day - 1]
        else:
            day_lineup[day] = lineups_by_team
            day_stlats[day] = stlats_by_team
            day_names[day] = names_by_team
            day_blood[day] = blood_by_team
            day_rotations[day] = rotations_by_team


def reset_daily_cache():
    global lineups_by_team
    global rotations_by_team
    global game_stats_by_team
    global stlats_by_team
    global names_by_team
    global blood_by_team
    lineups_by_team = {}
    rotations_by_team = {}
    stlats_by_team = {}
    names_by_team = {}
    blood_by_team = {}


def get_stlat_dict(player: Dict[str, Any]) -> Dict[FK, float]:
    ret_val: Dict[FK, float] = {}
    for k in fk_key:
        str_name = fk_key[k]
        ret_val[k] = float(player[str_name])
    return ret_val


def update_team_states(season: int, day: int, team:str, starting_pitcher: str, weather: Weather, is_home: bool):
    if team_id_map[team] not in team_states:
        team_states[team_id_map[team]] = TeamState(
            team_id=team,
            season=season,
            day=day,
            weather=weather,
            is_home=is_home,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup=day_lineup[day][team],
            rotation=day_rotations[day][team],
            starting_pitcher=starting_pitcher,
            stlats=day_stlats[day][team],
            game_stats=game_stats_by_team[team],
            blood=day_blood[day][team],
            player_names=day_names[day][team],
            cur_batter_pos=1,
        )
    else:
        team_states[team_id_map[team]].day = day
        team_states[team_id_map[team]].weather = weather
        team_states[team_id_map[team]].is_home = is_home
        team_states[team_id_map[team]].lineup = day_lineup[day][team]
        team_states[team_id_map[team]].rotation = day_rotations[day][team]
        team_states[team_id_map[team]].starting_pitcher = starting_pitcher
        team_states[team_id_map[team]].stlats = day_stlats[day][team]
        team_states[team_id_map[team]].blood = day_blood[day][team]
        #team_states[team_id_map[team]].player_names = day_names[day][team]
        team_states[team_id_map[team]].update_player_names(day_names[day][team])
        team_states[team_id_map[team]].reset_team_state()


def print_leaders():
    strikeouts = []
    hrs = []
    avg = []
    for cur_team in team_states.keys():
        for player in team_states[cur_team].game_stats.keys():
            if Stats.PITCHER_STRIKEOUTS in team_states[cur_team].game_stats[player]:
                player_name = team_states[cur_team].player_names[player]
                value = team_states[cur_team].game_stats[player][Stats.PITCHER_STRIKEOUTS] / float(iterations)
                strikeouts.append((value, player_name))
            if Stats.BATTER_HRS in team_states[cur_team].game_stats[player]:
                player_name = team_states[cur_team].player_names[player]
                value = team_states[cur_team].game_stats[player][Stats.BATTER_HRS] / float(iterations)
                hrs.append((value, player_name))
            if Stats.BATTER_HITS in team_states[cur_team].game_stats[player]:
                player_name = team_states[cur_team].player_names[player]
                hits = team_states[cur_team].game_stats[player][Stats.BATTER_HITS]
                abs = team_states[cur_team].game_stats[player][Stats.BATTER_AT_BATS]
                value = hits / abs
                avg.append((value, player_name))
    print("STRIKEOUTS")
    count = 0
    for value, name in reversed(sorted(strikeouts)):
        if count == 10:
            break
        print(f'\t{name}: {value}')
        count += 1
    print("HRS")
    count = 0
    for value, name in reversed(sorted(hrs)):
        if count == 10:
            break
        print(f'\t{name}: {value}')
        count += 1
    print("avg")
    count = 0
    for value, name in reversed(sorted(avg)):
        if count == 10:
            break
        print(f'\t{name}: {value:.3f}')
        count += 1

season = 11
#print_info()
load_all_state(season)
setup_season(season)
print_leaders()