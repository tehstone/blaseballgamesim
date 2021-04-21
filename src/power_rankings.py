import json
import os
import random
import time
from decimal import Decimal
from typing import Dict, List, Any

import requests
from requests import Timeout

from common import enabled_player_buffs, blaseball_weather_pretty_print_map
from common import ForbiddenKnowledge as FK
from common import BlaseballStatistics as Stats, blood_name_map
from common import BloodType, Team, blood_id_map, fk_key, PlayerBuff, Weather
from game_state import GameState, InningHalf
from stadium import Stadium
from team_state import TeamState, DEF_ID, TEAM_ID

team_ids = ["b72f3061-f573-40d7-832a-5ad475bd7909","878c1bf6-0d21-4659-bfee-916c8314d69c","b024e975-1c4a-4575-8936-a3754a08806a","adc5b394-8f76-416d-9ce9-813706877b84","ca3f1c8c-c025-4d8e-8eef-5be6accbeb16","bfd38797-8404-4b38-8b82-341da28b1f83","3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e","979aee4a-6d80-4863-bf1c-ee1a78e06024","7966eb04-efcc-499b-8f03-d13916330531","36569151-a2fb-43c1-9df7-2df512424c82","8d87c468-699a-47a8-b40d-cfb73a5660ad","9debc64f-74b7-4ae1-a4d6-fce0144b6ea5","23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7","f02aeae2-5e6a-4098-9842-02d2273f25c7","57ec08cc-0411-4643-b304-0e80dbc15ac7","747b8e4a-7e50-4638-a973-ea7950a3e739","eb67ae5e-c4bf-46ca-bbbc-425cd34182ff","b63be8c2-576a-4d6e-8daf-814f8bcea96f","105bc3ff-1320-4e37-8ef0-8d595cb95dd0","a37f9158-7f82-46bc-908c-c9e2dda7c33b","c73b705c-40ad-4633-a6ed-d357ee2e2bcf","d9f89a8a-c563-493e-9d64-78e4f9a55d4a","46358869-dce9-4a01-bfba-ac24fc56f57e","bb4a9de5-c924-4923-a0cb-9d1445f1ee5d"]
stadiums = {}
lineups_by_team: Dict[str, Dict[int, str]] = {}
rotations_by_team: Dict[str, Dict[int, str]] = {}
stlats_by_team: Dict[str, Dict[str, Dict[FK, float]]] = {}
buffs_by_team: Dict[str, Dict[str, Dict[PlayerBuff, int]]] = {}
game_stats_by_team: Dict[str, Dict[str, Dict[Stats, float]]] = {}
segmented_stats_by_team: Dict[str, Dict[int, Dict[str, Dict[Stats, float]]]] = {}
names_by_team: Dict[str, Dict[str, str]] = {}
blood_by_team: Dict[str, Dict[str, BloodType]] = {}
team_states: Dict[Team, TeamState] = {}
starting_pitchers: Dict[str, str] = {}
default_stadium: Stadium = Stadium(
    "team_id",
    "stadium_id",
    "stadium_name",
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    [],
)


def retry_request(url, tries=10):
    headers = {
        'User-Agent': 'sibrGameSim/0.1test (tehstone#8448@sibr)'
    }

    for i in range(tries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
        except (Timeout, Exception):
            continue
        finally:
            time.sleep(.5)
    return None


def get_stlat_dict(player: Dict[str, Any]) -> Dict[FK, float]:
    ret_val: Dict[FK, float] = {}
    for k in fk_key:
        str_name = fk_key[k]
        ret_val[k] = float(player[str_name])
    return ret_val


def get_current_player_stlats(season, day, team_ids):
    filename = os.path.join('..', 'season_sim', "stlats", f"bprm_s{season}_stlats.json")
    stlats_json = {}
    pitchers = {}
    batters = {}
    teams_response = retry_request("https://www.blaseball.com/database/allteams")
    teams_json = teams_response.json()
    for team in teams_json:
        if team["id"] not in team_ids:
            continue
        p_counter = 1
        b_counter = 1
        for pitcher in team["rotation"]:
            pitchers[pitcher] = {
                "position_id": p_counter,
                "position_type": "PITCHER"}
            p_counter += 1
        for batter in team["lineup"]:
            batters[batter] = {
                "position_id": b_counter,
                "position_type": "BATTER"
            }
            b_counter += 1
    pitcher_ids = list(pitchers.keys())
    chunked_pitcher_ids = [pitcher_ids[i:i + 50] for i in range(0, len(pitcher_ids), 50)]
    for chunk in chunked_pitcher_ids:
        b_url = f"https://www.blaseball.com/database/players?ids={','.join(chunk)}"
        pitcher_response = retry_request(b_url)
        pitcher_json = pitcher_response.json()
        for pitcher in pitcher_json:
            pitcher["position_id"] = pitchers[pitcher["id"]]["position_id"]
            pitcher["position_type"] = pitchers[pitcher["id"]]["position_type"]
            stlats_json[pitcher["id"]] = pitcher
    batter_ids = list(batters.keys())
    chunked_batter_ids = [batter_ids[i:i + 50] for i in range(0, len(batter_ids), 50)]
    for chunk in chunked_batter_ids:
        b_url = f"https://www.blaseball.com/database/players?ids={','.join(chunk)}"
        batter_response = retry_request(b_url)
        batter_json = batter_response.json()
        for batter in batter_json:
            batter["position_id"] = batters[batter["id"]]["position_id"]
            batter["position_type"] = batters[batter["id"]]["position_type"]
            stlats_json[batter["id"]] = batter
    with open(filename, 'w', encoding='utf8') as json_file:
        json.dump(stlats_json, json_file)
    return stlats_json


def setup_stlats(season: int, day: int, team_ids: List):
    player_stlats_list = get_current_player_stlats(season, day, team_ids)
    for player_id, player in player_stlats_list.items():
        plus_pos = False
        if "leagueTeamId" in player:
            team_id = player["leagueTeamId"]
        else:
            plus_pos = True
            team_id = player["team_id"]
        pos = int(player["position_id"])
        if plus_pos:
            pos += 1
        if "position_type_id" in player:
            if player["position_type_id"] == "0":
                if team_id not in lineups_by_team:
                    lineups_by_team[team_id] = {}
                lineups_by_team[team_id][pos] = player_id
            else:
                if team_id not in starting_pitchers:
                    starting_pitchers[team_id] = player_id
                if team_id not in rotations_by_team:
                    rotations_by_team[team_id] = {}
                rotations_by_team[team_id][pos] = player_id

        else:
            if player["position_type"] == "BATTER":
                if team_id not in lineups_by_team:
                    lineups_by_team[team_id] = {}
                lineups_by_team[team_id][pos] = player_id
            else:
                if team_id not in starting_pitchers:
                    starting_pitchers[team_id] = player_id
                if team_id not in rotations_by_team:
                    rotations_by_team[team_id] = {}
                rotations_by_team[team_id][pos] = player_id

        if team_id not in stlats_by_team:
            stlats_by_team[team_id] = {}
        stlats_by_team[team_id][player_id] = get_stlat_dict(player)

        if "permAttr" in player:
            mods = player["permAttr"]
        elif "modifications" in player:
            mods = player["modifications"]
        else:
            mods = None
        cur_mod_dict = {}
        if mods:
            for mod in mods:
                if mod in enabled_player_buffs:
                    if PlayerBuff[mod] == PlayerBuff.ELSEWHERE:
                        continue
                    cur_mod_dict[PlayerBuff[mod]] = 1
            if player_id == "4b3e8e9b-6de1-4840-8751-b1fb45dc5605":
                cur_mod_dict[PlayerBuff.BLASERUNNING] = 1
        if team_id not in buffs_by_team:
            buffs_by_team[team_id] = {}
        buffs_by_team[team_id][player_id] = cur_mod_dict

        if team_id not in game_stats_by_team:
            game_stats_by_team[team_id] = {}
            game_stats_by_team[team_id][DEF_ID] = {}
            game_stats_by_team[team_id][TEAM_ID] = {}
        game_stats_by_team[team_id][player_id] = {}

        if team_id not in segmented_stats_by_team:
            segmented_stats_by_team[team_id] = {}

        if team_id not in names_by_team:
            names_by_team[team_id] = {}
        if "name" in player:
            names_by_team[team_id][player_id] = player["name"]
        else:
            names_by_team[team_id][player_id] = player["player_name"]

        if team_id not in blood_by_team:
            blood_by_team[team_id] = {}
        try:
            blood_by_team[team_id][player_id] = blood_id_map[int(player["blood"])]
        except ValueError:
            blood_by_team[team_id][player_id] = blood_name_map[player["blood"]]
        except TypeError:
            blood_by_team[team_id][player_id] = BloodType.A


def load_all_state(season: int):
    setup_stlats(season, -1, team_ids)

    with open(os.path.join('..', 'season_sim', "ballparks.json"), 'r', encoding='utf8') as json_file:
        ballparks = json.load(json_file)
    for team in ballparks.keys():
        team_id = ballparks[team]["data"]["teamId"]
        stadium = Stadium.from_ballpark_json(ballparks[team])
        stadiums[team_id] = stadium

    for team in team_ids:
        pitcher = rotations_by_team[team][1]
        team_state = make_team_state(team, pitcher, stadiums[team], season, 0)
        team_state.reset_team_state(game_stat_reset=True)
        team_states[team] = team_state


def pick_weather():
    pick = random.randint(1, 1188)
    if pick <= 226:
        return Weather.SALMON
    if pick <= 338:
        return Weather.ECLIPSE
    if pick <= 439:
        return Weather.BLACKHOLE
    if pick <= 724:
        return Weather.FLOODING
    if pick <= 831:
        return Weather.SUN2
    if pick <= 861:
        return Weather.BIRD
    if pick <= 884:
        return Weather.COFFEE3
    if pick <= 900:
        return Weather.COFFEE2
    if pick <= 960:
        return Weather.PEANUTS
    if pick <= 1033:
        return Weather.REVERB
    if pick <= 1069:
        return Weather.BLOODDRAIN
    if pick <= 1105:
        return Weather.COFFEE
    if pick <= 1167:
        return Weather.FEEDBACK
    if pick <= 1188:
        return Weather.GLITTER


def run_single_bprm(team_id, o_team, iterations, all_weathers, count):
    pitchers = {team_id: [], o_team: []}
    results = {team_id: {"wins": 0, "losses": 0}, o_team: {"wins": 0, "losses": 0}}
    half = round(iterations / 2)

    t1 = round(time.time())
    print(f"{count} Running {iterations} sims of {team_id} vs {o_team}. st: {t1}")

    home_team_state = team_states[team_id]
    away_team_state = team_states[o_team]
    home_team_state.cur_pitcher_pos = 1
    away_team_state.cur_pitcher_pos = 1
    home_team_state.reset_team_state()
    away_team_state.reset_team_state()
    run_iters(results, home_team_state, away_team_state, half, pitchers, all_weathers)

    away_team_state = team_states[team_id]
    home_team_state = team_states[o_team]
    run_iters(results, home_team_state, away_team_state, half, pitchers, all_weathers)

    t2 = round(time.time())
    print(f"{team_id} vs {o_team} complete at {t2}. elapsed: {t2-t1}")
    return results, pitchers


def run_iters(results, home_team, away_team, half, pitchers, all_weathers):
    for day in range(half):
        day = day % 99

        home_team.day = day
        away_team.day = day
        pitchers[home_team.team_id].append(home_team.player_names[home_team.starting_pitcher])
        pitchers[away_team.team_id].append(away_team.player_names[away_team.starting_pitcher])

        weather = pick_weather()
        if weather:
            all_weathers[weather] += 1
        else:
            print("wtf no weather")
            weather = Weather.ECLIPSE
        game_sim = GameState(
            game_id='',
            season=15,
            day=day,
            stadium=home_team.stadium,
            home_team=home_team,
            away_team=away_team,
            home_score=Decimal("0"),
            away_score=Decimal("0"),
            inning=1,
            half=InningHalf.TOP,
            outs=0,
            strikes=0,
            balls=0,
            weather=weather,
            old_models=False,
        )
        game_sim.simulate_game()
        if game_sim.home_score > game_sim.away_score:
            results[home_team.team_id]["wins"] += 1
            results[away_team.team_id]["losses"] += 1
        else:
            results[away_team.team_id]["wins"] += 1
            results[home_team.team_id]["losses"] += 1
        home_team.next_pitcher()
        home_team.reset_team_state()
        away_team.next_pitcher()
        away_team.reset_team_state()


team_name_map: Dict[str, str] = {
    "b72f3061-f573-40d7-832a-5ad475bd7909": "lovers",
    "878c1bf6-0d21-4659-bfee-916c8314d69c": "tacos",
    "b024e975-1c4a-4575-8936-a3754a08806a": "steaks",
    "adc5b394-8f76-416d-9ce9-813706877b84": "breath mints",
    "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16": "firefighters",
    "bfd38797-8404-4b38-8b82-341da28b1f83": "shoe thieves",
    "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e": "flowers",
    "979aee4a-6d80-4863-bf1c-ee1a78e06024": "fridays",
    "7966eb04-efcc-499b-8f03-d13916330531": "magic",
    "36569151-a2fb-43c1-9df7-2df512424c82": "millennials",
    "8d87c468-699a-47a8-b40d-cfb73a5660ad": "crabs",
    "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5": "spies",
    "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7": "pies",
    "f02aeae2-5e6a-4098-9842-02d2273f25c7": "sunbeams",
    "57ec08cc-0411-4643-b304-0e80dbc15ac7": "wild wings",
    "747b8e4a-7e50-4638-a973-ea7950a3e739": "tigers",
    "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff": "moist talkers",
    "b63be8c2-576a-4d6e-8daf-814f8bcea96f": "dale",
    "105bc3ff-1320-4e37-8ef0-8d595cb95dd0": "garages",
    "a37f9158-7f82-46bc-908c-c9e2dda7c33b": "jazz hands",
    "c73b705c-40ad-4633-a6ed-d357ee2e2bcf": "lift",
    "d9f89a8a-c563-493e-9d64-78e4f9a55d4a": "georgias",
    "46358869-dce9-4a01-bfba-ac24fc56f57e": "mechanics",
    "bb4a9de5-c924-4923-a0cb-9d1445f1ee5d": "worms",
}


def run_sim(season, iterations):
    t1 = round(time.time())
    with open(os.path.join('..', 'season_sim', 'bprm', 'matches.json'), 'r') as file:
        matchups = json.load(file)
    count = 0
    all_pitchers = {}
    all_weathers = {
        Weather.SUN2: 0,
        Weather.ECLIPSE: 0,
        Weather.BLOODDRAIN: 0,
        Weather.PEANUTS: 0,
        Weather.BIRD: 0,
        Weather.FEEDBACK: 0,
        Weather.REVERB: 0,
        Weather.BLACKHOLE: 0,
        Weather.COFFEE: 0,
        Weather.COFFEE2: 0,
        Weather.COFFEE3: 0,
        Weather.FLOODING: 0,
        Weather.SALMON: 0,
        Weather.GLITTER: 0,
    }
    results = {}
    for team in matchups:
        team_id = team["team_id"]
        team_name = team["team_name"]
        all_pitchers[team_id] = []
        results[team_name] = {}
        for o_team in team["matches"]:
            o_team_name = team_name_map[o_team]
            if o_team_name not in results:
                results[o_team_name] = {}
            if o_team not in all_pitchers:
                all_pitchers[o_team] = []
            already_run = False
            results[team_name][o_team_name] = {}
            if o_team_name in results:
                if team_name in results[o_team_name]:
                    already_run = True
                    results[team_name][o_team_name] = results[o_team_name][team_name]
            if already_run:
                continue
            count += 1
            result, pitchers = run_single_bprm(team_id, o_team, iterations, all_weathers, count)
            all_pitchers[team_id].append(pitchers[team_id])
            all_pitchers[o_team].append(pitchers[o_team])
            results[team_name][o_team_name] = result
            results[o_team_name][team_name] = result
    with open(os.path.join('..', 'season_sim', 'bprm', f'{season}_{iterations}_iter_results.json'), 'w') as file:
        json.dump(results, file)
    with open(os.path.join('..', 'season_sim', 'bprm', f'{season}_{iterations}_iter_all_pitchers.json'), 'w') as file:
        json.dump(all_pitchers, file)
    with open(os.path.join('..', 'season_sim', 'bprm', 'weathers.json'), 'w') as file:
        json.dump(convert_keys(all_weathers), file)
    t2 = round(time.time())
    print(f"finished run in {round(t2-t1)} seconds. {count} total team v team sims.")


def make_team_state(team, pitcher, stadium, season, day):
    return TeamState(
        team_id=team,
        season=season,
        day=day,
        stadium=stadium,
        weather=Weather.SUN2,
        is_home=True,
        num_bases=4,
        balls_for_walk=4,
        strikes_for_out=3,
        outs_for_inning=3,
        lineup=lineups_by_team[team],
        rotation=rotations_by_team[team],
        starting_pitcher=pitcher,
        cur_pitcher_pos=1,
        stlats=stlats_by_team[team],
        buffs=buffs_by_team[team],
        game_stats=game_stats_by_team[team],
        segmented_stats=segmented_stats_by_team[team],
        blood=blood_by_team[team],
        player_names=names_by_team[team],
        cur_batter_pos=1,
    )

def convert_keys(obj, convert=str):
    if isinstance(obj, list):
        return [convert_keys(i, convert) for i in obj]
    if not isinstance(obj, dict):
        return obj
    ret_dict = {}
    for k, v in obj.items():
        k = blaseball_weather_pretty_print_map[k] if isinstance(k, Weather) else convert(k)
        ret_dict[k] = convert_keys(v, convert)
    return ret_dict


def run_power_ranking_sim(season, iterations):
    print(f"running power rank sim with {iterations} iterations.")
    t1 = round(time.time())
    load_all_state(season)
    t2 = round(time.time())
    print(f"State set up complete in {t2 - t1}")
    run_sim(season, iterations)
    team_id_name_map: Dict[str, str] = {
            "lovers": "b72f3061-f573-40d7-832a-5ad475bd7909",
            "tacos": "878c1bf6-0d21-4659-bfee-916c8314d69c",
            "steaks": "b024e975-1c4a-4575-8936-a3754a08806a",
            "breath mints": "adc5b394-8f76-416d-9ce9-813706877b84",
            "firefighters": "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16",
            "shoe thieves": "bfd38797-8404-4b38-8b82-341da28b1f83",
            "flowers": "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e",
            "fridays": "979aee4a-6d80-4863-bf1c-ee1a78e06024",
            "magic": "7966eb04-efcc-499b-8f03-d13916330531",
            "millennials": "36569151-a2fb-43c1-9df7-2df512424c82",
            "crabs": "8d87c468-699a-47a8-b40d-cfb73a5660ad",
            "spies": "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5",
            "pies": "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7",
            "sunbeams": "f02aeae2-5e6a-4098-9842-02d2273f25c7",
            "wild wings": "57ec08cc-0411-4643-b304-0e80dbc15ac7",
            "tigers": "747b8e4a-7e50-4638-a973-ea7950a3e739",
            "moist talkers": "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff",
            "dale": "b63be8c2-576a-4d6e-8daf-814f8bcea96f",
            "garages": "105bc3ff-1320-4e37-8ef0-8d595cb95dd0",
            "jazz hands": "a37f9158-7f82-46bc-908c-c9e2dda7c33b",
            "lift": "c73b705c-40ad-4633-a6ed-d357ee2e2bcf",
            "georgias": "d9f89a8a-c563-493e-9d64-78e4f9a55d4a",
            "mechanics": "46358869-dce9-4a01-bfba-ac24fc56f57e",
            "worms": "bb4a9de5-c924-4923-a0cb-9d1445f1ee5d",
        }
    with open(os.path.join('..', 'season_sim', 'bprm', f'{season}_{iterations}_iter_results.json'), 'r') as file:
        results = json.load(file)
    output = ""
    for team in results:
        team_id = team_id_name_map[team]
        team_wins = 0
        for opp in results[team].values():
            team_wins += opp[team_id]["wins"]

        output += f"{team}\t{team_wins}\n"
    return {"output": output}

def print_results():
    with open(os.path.join('..', 'season_sim', 'bprm', f'16_51_iter_results.json'), 'r') as file:
        results = json.load(file)
    output = ""
    team_id_name_map: Dict[str, str] = {
        "lovers": "b72f3061-f573-40d7-832a-5ad475bd7909",
        "tacos": "878c1bf6-0d21-4659-bfee-916c8314d69c",
        "steaks": "b024e975-1c4a-4575-8936-a3754a08806a",
        "breath mints": "adc5b394-8f76-416d-9ce9-813706877b84",
        "firefighters": "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16",
        "shoe thieves": "bfd38797-8404-4b38-8b82-341da28b1f83",
        "flowers": "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e",
        "fridays": "979aee4a-6d80-4863-bf1c-ee1a78e06024",
        "magic": "7966eb04-efcc-499b-8f03-d13916330531",
        "millennials": "36569151-a2fb-43c1-9df7-2df512424c82",
        "crabs": "8d87c468-699a-47a8-b40d-cfb73a5660ad",
        "spies": "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5",
        "pies": "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7",
        "sunbeams": "f02aeae2-5e6a-4098-9842-02d2273f25c7",
        "wild wings": "57ec08cc-0411-4643-b304-0e80dbc15ac7",
        "tigers": "747b8e4a-7e50-4638-a973-ea7950a3e739",
        "moist talkers": "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff",
        "dale": "b63be8c2-576a-4d6e-8daf-814f8bcea96f",
        "garages": "105bc3ff-1320-4e37-8ef0-8d595cb95dd0",
        "jazz hands": "a37f9158-7f82-46bc-908c-c9e2dda7c33b",
        "lift": "c73b705c-40ad-4633-a6ed-d357ee2e2bcf",
        "georgias": "d9f89a8a-c563-493e-9d64-78e4f9a55d4a",
        "mechanics": "46358869-dce9-4a01-bfba-ac24fc56f57e",
        "worms": "bb4a9de5-c924-4923-a0cb-9d1445f1ee5d",
    }
    for team in results:
        team_id = team_id_name_map[team]
        team_wins = 0
        for opp in results[team].values():
            team_wins += opp[team_id]["wins"]

        print(f"{team}\t{team_wins}")
    return {"output": output}
#run_power_ranking_sim(16, 51)
#print_results()