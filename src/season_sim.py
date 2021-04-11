from decimal import Decimal
from os import path
from typing import Any, Dict
import os
import json
import time

from common import get_stlats_for_season, blood_name_map, PlayerBuff, enabled_player_buffs, convert_keys
from common import BlaseballStatistics as Stats
from common import ForbiddenKnowledge as FK
from common import BloodType, Team, team_id_map, blood_id_map, fk_key, Weather, team_name_map
from daily_sim import retry_request
from stadium import Stadium
from team_state import TeamState, DEF_ID, TEAM_ID
from game_state import GameState, InningHalf

lineups_by_team: Dict[str, Dict[int, str]] = {}
stlats_by_team: Dict[str, Dict[str, Dict[FK, float]]] = {}
buffs_by_team: Dict[str, Dict[str, Dict[PlayerBuff, int]]] = {}
game_stats_by_team: Dict[str, Dict[str, Dict[Stats, float]]] = {}
segmented_stats_by_team: Dict[str, Dict[int, Dict[str, Dict[Stats, float]]]] = {}
names_by_team: Dict[str, Dict[str, str]] = {}
blood_by_team: Dict[str, Dict[str, BloodType]] = {}
team_states: Dict[Team, TeamState] = {}
rotations_by_team: Dict[str, Dict[int, str]] = {}
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
)

day_lineup = {}
day_stlats = {}
day_buffs = {}
day_names = {}
day_blood = {}
day_rotations = {}
stadiums = {}


def setup_season(season:int, stats_segment_size:int, iterations:int):
    with open(os.path.join('..', 'season_sim', 'season_data', f"season{season + 1}.json"), 'r', encoding='utf8') as json_file:
        raw_season_data = json.load(json_file)
    failed = 0
    team_records = {}
    last_day = 0
    for game in raw_season_data:
        home_team_name = game["homeTeamName"]
        away_team_name = game["awayTeamName"]
        day = int(game["day"])
        if day != last_day:
            last_day = day
            print(f"Starting day: {day}")
        # try:
        game_id = game["id"]
        home_pitcher = game["homePitcher"]
        away_pitcher = game["awayPitcher"]
        home_team = game["homeTeam"]
        away_team = game["awayTeam"]

        home_odds = game["homeOdds"]
        away_odds = game["awayOdds"]

        if home_team not in team_records:
            team_records[home_team] = {"wins": 0, "losses": 0, "days": []}
        if away_team not in team_records:
            team_records[away_team] = {"wins": 0, "losses": 0, "days": []}

        weather = Weather(game["weather"])

        if day == 99:
            break
        update_team_states(season, day, home_team, home_pitcher, weather, True, stats_segment_size)
        home_team_state = team_states[team_id_map[home_team]]
        update_team_states(season, day, away_team, away_pitcher, weather, False, stats_segment_size)
        away_team_state = team_states[team_id_map[away_team]]
        game_state = GameState(
            game_id=game_id,
            season=season,
            day=day,
            stadium=home_team_state.stadium,
            home_team=home_team_state,
            away_team=away_team_state,
            home_score=Decimal("0"),
            away_score=Decimal("0"),
            inning=1,
            half=InningHalf.TOP,
            outs=0,
            strikes=0,
            balls=0,
            weather=weather
        )
        home_wins, away_wins = 0, 0
        for x in range(0, iterations):
            home_score, away_score = game_state.simulate_game()
            if home_score > away_score:
                home_wins += 1
            else:
                away_wins += 1
            game_state.reset_game_state()

        home_odds_str = round(home_odds * 1000) / 10
        away_odds_str = round(away_odds * 1000) / 10
        home_win = home_wins > away_wins
        away_win = home_wins < away_wins
        team_records[home_team]["days"].append({
            "pitcher": game_state.home_team.player_names[game_state.home_team.starting_pitcher],
            "opponent": away_team_name,
            "opponent_pitcher": game_state.away_team.player_names[game_state.away_team.starting_pitcher],
            "weather": game["weather"],
            "win": home_win
        })
        team_records[away_team]["days"].append({
            "pitcher": game_state.away_team.player_names[game_state.away_team.starting_pitcher],
            "opponent": home_team_name,
            "opponent_pitcher": game_state.home_team.player_names[game_state.home_team.starting_pitcher],
            "weather": game["weather"],
            "win": away_win
        })
        if home_win:
            team_records[home_team]["wins"] += 1
            team_records[away_team]["losses"] += 1
        else:
            team_records[away_team]["wins"] += 1
            team_records[home_team]["losses"] += 1

    filename = os.path.join('..', 'season_sim', 'results', f'{round(time.time())}_team_records_s{season}.json')
    with open(filename, 'w') as file:
        json.dump(team_records, file)
    return team_records


def get_current_stlats(season):
    stlats_json = {}
    pitchers = {}
    batters = {}
    teams_response = retry_request("https://www.blaseball.com/database/allteams")
    teams_json = teams_response.json()
    team_ids = ["b72f3061-f573-40d7-832a-5ad475bd7909", "878c1bf6-0d21-4659-bfee-916c8314d69c",
                "b024e975-1c4a-4575-8936-a3754a08806a", "adc5b394-8f76-416d-9ce9-813706877b84",
                "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16", "bfd38797-8404-4b38-8b82-341da28b1f83",
                "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e", "979aee4a-6d80-4863-bf1c-ee1a78e06024",
                "7966eb04-efcc-499b-8f03-d13916330531", "36569151-a2fb-43c1-9df7-2df512424c82",
                "8d87c468-699a-47a8-b40d-cfb73a5660ad", "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5",
                "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7", "f02aeae2-5e6a-4098-9842-02d2273f25c7",
                "57ec08cc-0411-4643-b304-0e80dbc15ac7", "747b8e4a-7e50-4638-a973-ea7950a3e739",
                "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff", "b63be8c2-576a-4d6e-8daf-814f8bcea96f",
                "105bc3ff-1320-4e37-8ef0-8d595cb95dd0", "a37f9158-7f82-46bc-908c-c9e2dda7c33b",
                "c73b705c-40ad-4633-a6ed-d357ee2e2bcf", "d9f89a8a-c563-493e-9d64-78e4f9a55d4a",
                "46358869-dce9-4a01-bfba-ac24fc56f57e", "bb4a9de5-c924-4923-a0cb-9d1445f1ee5d"]
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
            if "baseThirst" in pitcher:
                pitcher["base_thirst"] = pitcher["baseThirst"]
            if "groundFriction" in pitcher:
                pitcher["ground_friction"] = pitcher["groundFriction"]
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
            if "baseThirst" in batter:
                batter["base_thirst"] = batter["baseThirst"]
            if "groundFriction" in batter:
                batter["ground_friction"] = batter["groundFriction"]
            batter["position_id"] = batters[batter["id"]]["position_id"]
            batter["position_type"] = batters[batter["id"]]["position_type"]
            stlats_json[batter["id"]] = batter

    filename = os.path.join('..', 'season_sim', 'stlats', f's{season}_preseason_stlats.json')
    with open(filename, 'w', encoding='utf8') as json_file:
        json.dump(stlats_json, json_file)
    return stlats_json

def load_all_state(season: int, future=False):
    if not future:
        if not path.exists(os.path.join('..', 'season_sim', 'stlats', f"s{season}_d98_stlats.json")):
            get_stlats_for_season(season)

    with open(os.path.join('..', 'season_sim', "ballparks.json"), 'r', encoding='utf8') as json_file:
        ballparks = json.load(json_file)
    for team in ballparks.keys():
        team_id = ballparks[team]["data"]["teamId"]
        stadium = Stadium.from_ballpark_json(ballparks[team])
        stadiums[team_id] = stadium

    for day in range(0, 99):
        reset_daily_cache()
        if future:
            filename = os.path.join('..', 'season_sim', 'stlats', f"s{season}_preseason_stlats.json")
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf8') as json_file:
                    player_stlats = json.load(json_file)
            else:
                player_stlats = get_current_stlats(season)
        else:
            filename = os.path.join('..', 'season_sim', 'stlats', f"s{season}_d{day}_stlats.json")
            with open(filename, 'r', encoding='utf8') as json_file:
                player_stlats_list = json.load(json_file)
        for pid, player in player_stlats.items():
            plus_pos = False
            if "leagueTeamId" in player:
                team_id = player["leagueTeamId"]
            else:
                plus_pos = True
                team_id = player["team_id"]
            pos = int(player["position_id"])
            if plus_pos:
                pos += 1
            player_id = pid
            #pos = int(player["position_id"]) + 1
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
                        cur_mod_dict[PlayerBuff[mod]] = 1
                if player_id == "4b3e8e9b-6de1-4840-8751-b1fb45dc5605":
                    cur_mod_dict[PlayerBuff.BLASERUNNING] = 1
            if team_id not in buffs_by_team:
                buffs_by_team[team_id] = {}
            buffs_by_team[team_id][player_id] = cur_mod_dict

            if team_id not in game_stats_by_team:
                game_stats_by_team[team_id] = {}
                game_stats_by_team[team_id][DEF_ID] = {}
            game_stats_by_team[team_id][player_id] = {}

            if team_id not in segmented_stats_by_team:
                segmented_stats_by_team[team_id] = {}

            if team_id not in names_by_team:
                names_by_team[team_id] = {}
            if "player_name" in player:
                names_by_team[team_id][player_id] = player["player_name"]
            else:
                names_by_team[team_id][player_id] = player["name"]

            if team_id not in blood_by_team:
                blood_by_team[team_id] = {}
            try:
                blood_by_team[team_id][player_id] = blood_id_map[int(player["blood"])]
            except ValueError:
                blood_by_team[team_id][player_id] = blood_name_map[player["blood"]]
            except TypeError:
                blood_by_team[team_id][player_id] = BloodType.A

        if day > 0 and (len(lineups_by_team) != len(day_lineup[day - 1]) or (len(rotations_by_team) != len(day_rotations[day - 1]))):
            day_lineup[day] = day_lineup[day-1]
            day_stlats[day] = day_stlats[day-1]
            day_buffs[day] = day_buffs[day-1]
            day_names[day] = day_names[day-1]
            day_blood[day] = day_blood[day-1]
            day_rotations[day] = day_rotations[day - 1]
        else:
            day_lineup[day] = lineups_by_team
            day_stlats[day] = stlats_by_team
            day_buffs[day] = buffs_by_team
            day_names[day] = names_by_team
            day_blood[day] = blood_by_team
            day_rotations[day] = rotations_by_team


def reset_daily_cache():
    global lineups_by_team
    global rotations_by_team
    global game_stats_by_team
    global segmented_stats_by_team
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


def update_team_states(season: int, day: int, team: str, starting_pitcher: str,
                       weather: Weather, is_home: bool, stats_segment_size: int):
    if team_id_map[team] not in team_states:
        if team in stadiums:
            stadium = stadiums[team]
        else:
            stadium = default_stadium
        if not starting_pitcher:
            starting_pitcher = day_rotations[day][team][1]
        team_states[team_id_map[team]] = TeamState(
            team_id=team,
            season=season,
            day=day,
            stadium=stadium,
            weather=weather,
            is_home=is_home,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup=day_lineup[day][team],
            rotation=day_rotations[day][team],
            starting_pitcher=starting_pitcher,
            cur_pitcher_pos=1,
            stlats=day_stlats[day][team],
            buffs=day_buffs[day][team],
            game_stats=game_stats_by_team[team],
            segmented_stats=segmented_stats_by_team[team],
            blood=day_blood[day][team],
            player_names=day_names[day][team],
            cur_batter_pos=1,
            segment_size=stats_segment_size,
        )
    else:
        team_states[team_id_map[team]].day = day
        team_states[team_id_map[team]].weather = weather
        team_states[team_id_map[team]].is_home = is_home
        # lineup_changed = False
        # if team_states[team_id_map[team]].lineup != day_lineup[day][team]:
        #     lineup_changed = True
        team_states[team_id_map[team]].lineup = day_lineup[day][team]
        team_states[team_id_map[team]].rotation = day_rotations[day][team]
        rotation_idx = team_states[team_id_map[team]].next_pitcher()
        team_states[team_id_map[team]].cur_pitcher_pos = rotation_idx
        if starting_pitcher:
            team_states[team_id_map[team]].starting_pitcher = starting_pitcher
        else:
            team_states[team_id_map[team]].starting_pitcher = team_states[team_id_map[team]].rotation[rotation_idx]
        team_states[team_id_map[team]].stlats = day_stlats[day][team]
        team_states[team_id_map[team]].player_buffs = day_buffs[day][team]
        team_states[team_id_map[team]].blood = day_blood[day][team]
        #team_states[team_id_map[team]].player_names = day_names[day][team]
        team_states[team_id_map[team]].update_player_names(day_names[day][team])
        team_states[team_id_map[team]].reset_team_state(lineup_changed=True)


def print_leaders(iterations, season):
    strikeouts = []
    hrs = []
    avg = []
    all_segmented_stats = {}
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
        for day, stats in team_states[cur_team].segmented_stats.items():
            if day not in all_segmented_stats:
                all_segmented_stats[day] = {}
            for player_id, player_stats in stats.items():
                if player_id not in team_states[cur_team].player_names:
                    continue
                all_segmented_stats[day][player_id] = {"name": team_states[cur_team].player_names[player_id]}
                for stat in [Stats.PITCHER_STRIKEOUTS, Stats.BATTER_HITS, Stats.BATTER_HRS, Stats.STOLEN_BASES]:
                    if stat in player_stats:
                        all_segmented_stats[day][player_id][stat] = player_stats[stat] / float(iterations)
    seg_stats_file = os.path.join("..", "season_sim", "results", f"{round(time.time())}_all_segmented_stats_s{season}.json")
    seg_stats_pretty = convert_keys(all_segmented_stats)
    with open(seg_stats_file, 'w') as f:
        json.dump(seg_stats_pretty, f)

    leader_msg = "STRIKEOUTS\n"
    count = 0
    for value, name in reversed(sorted(strikeouts)):
        if count == 10:
            break
        leader_msg += f'\t{name}: {value}\n'
        count += 1
    leader_msg += "HRS\n"
    count = 0
    for value, name in reversed(sorted(hrs)):
        if count == 10:
            break
        leader_msg += f'\t{name}: {value}\n'
        count += 1
    leader_msg += "avg\n"
    count = 0
    for value, name in reversed(sorted(avg)):
        if count == 10:
            break
        leader_msg += f'\t{name}: {value:.3f}\n'
        count += 1
    leaders_file = os.path.join('..', 'season_sim', 'results', f'{round(time.time())}_leaders_s{season}.txt')
    with open(leaders_file, 'w') as file:
        file.write(leader_msg)
    return seg_stats_pretty, leader_msg


def run_season_sim(season: int, iterations: int = 250,  stats_segment_size: int = 3, future=False):
    print(f"running season {season} sim with {iterations} iterations.")
    load_all_state(season, future)
    team_records = setup_season(season, stats_segment_size, iterations)
    seg_stats, leaders = print_leaders(iterations, season)
    return {"team_records": team_records, "seg_stats": seg_stats, "leaders": leaders}


#get_stlats_for_season(14)


#run_season_sim(season, iterations, stats_segment_size)

# def findall(pattern, string):
#     while True:
#         match = re.search(pattern, string)
#         if not match:
#             break
#         yield (match.group(1), match.group(2))
#         string = string[match.end():]
#
# day = 0
# team_outcomes = {}
# with open('season15preview.txt') as file:
#     lines = file.readlines()
# for line in lines:
#     if line.startswith('Day'):
#         matches = re.search(r'Day ([0-9]+)', line)
#         if matches:
#             day = int(matches.group(1)[0])
#     else:
#         matches = findall(r"([a-zA-Z ']+): ([0-9]+) \([0-9\.]+\) \- [0-9\.%]+", line)
#         if matches:
#             for m in matches:
#                 team = m[0].strip()
#                 wins = m[1]
#                 if team not in team_outcomes:
#                     team_outcomes[team] = {}
#                     team_outcomes[team]["days"] = {}
#                     team_outcomes[team]["wins"] = 0
#                 team_outcomes[team]["days"][day] = wins
#                 if int(wins) > 50:
#                     team_outcomes[team]["wins"] += 1
#
# for team, data in team_outcomes.items():
#     print(f"{team} {data['wins']} wins")

# for day in range(0, 62):
#     filepath = os.path.join('..', 'season_sim', 'results', f's14_d{day}_sim_results.json')
#     with open(filepath) as file:
#         results = json.load(file)
#     new_data = {}
#     for gid, game in results["data"].items():
#         new_game, new_home_team, new_away_team = {}, {}, {}
#         home_team, away_team = None, None
#         try:
#             for tid, team in game["teams"].items():
#                 if tid == team["game_info"]["homeTeam"]:
#                     home_team = team
#                 else:
#                     away_team = team
#         except KeyError:
#             continue
#         new_game["id"] = gid
#         new_game["weather"] = game['weather']
#         new_game["upset"] = home_team["upset"] or away_team["upset"]
#         new_game["win_percentage"] = max(home_team["win_percentage"], away_team["win_percentage"])
#         new_game["odds"] = max(home_team["game_info"]["homeOdds"], home_team["game_info"]["awayOdds"])
#         new_home_team["over_ten"] = home_team["over_ten"]
#         new_home_team["over_twenty"] = home_team["over_twenty"]
#         new_home_team["shutout_percentage"] = home_team["shutout_percentage"]
#         new_home_team["strikeout_avg"] = home_team["strikeout_avg"]
#         new_home_team["win"] = home_team["win"]
#         new_home_team["win_percentage"] = home_team["win_percentage"]
#         new_home_team["odds"] = home_team["game_info"]["homeOdds"]
#         new_home_team["team_id"] = home_team["game_info"]["homeTeam"]
#         new_home_team["team_name"] = home_team["game_info"]["homeTeamName"]
#         if home_team["opp_pitcher"]["p_team_id"] != new_home_team["team_id"]:
#             new_home_team["opp_pitcher"] = home_team["opp_pitcher"]
#         else:
#             new_home_team["opp_pitcher"] = away_team["opp_pitcher"]
#
#         new_away_team["over_ten"] = away_team["over_ten"]
#         new_away_team["over_twenty"] = away_team["over_twenty"]
#         new_away_team["shutout_percentage"] = away_team["shutout_percentage"]
#         new_away_team["strikeout_avg"] = away_team["strikeout_avg"]
#         new_away_team["win"] = away_team["win"]
#         new_away_team["win_percentage"] = away_team["win_percentage"]
#         new_away_team["odds"] = away_team["game_info"]["awayOdds"]
#         new_away_team["team_id"] = away_team["game_info"]["awayTeam"]
#         new_away_team["team_name"] = away_team["game_info"]["awayTeamName"]
#         if away_team["opp_pitcher"]["p_team_id"] != new_away_team["team_id"]:
#             new_away_team["opp_pitcher"] = away_team["opp_pitcher"]
#         else:
#             new_away_team["opp_pitcher"] = home_team["opp_pitcher"]
#
#         new_game["away_team"] = {
#             away_team["game_info"]["awayTeam"]: new_away_team
#         }
#         new_game["away_team"] = {
#             home_team["game_info"]["homeTeam"]: new_home_team
#         }
#
#         new_data[gid] = new_game
#     results["data"] = new_data
#     with open(filepath, 'w') as file:
#         json.dump(results, file)

# with open(os.path.join('..', 'season_sim', 'ballpark_issues', 'old.txt')) as file:
#     old_lines = file.readlines()
# with open(os.path.join('..', 'season_sim', 'ballpark_issues', 'new.txt')) as file:
#     new_lines = file.readlines()

# days = {}
# idx = 0
# for line in old_lines:
#     if line.startswith('Day'):
#         day = int(line.split(' ')[1])
#         days[day] = {"old_upset_only": 0, "new_upset_only": 0, "both_upset": 0}
#     else:
#         o_result = line.split(' ')[0]
#         n_result = new_lines[idx].split(' ')[0]
#         if o_result == "UPSET":
#             if n_result == "UPSET":
#                 days[day]["both_upset"] += 1
#             else:
#                 days[day]["old_upset_only"] += 1
#         else:
#             if n_result == "UPSET":
#                 days[day]["new_upset_only"] += 1
#
#     idx += 1
#
# with open(os.path.join('..', 'season_sim', 'ballpark_issues', 'upset_changes.json'),'w') as file:
#     json.dump(days, file)
#
# old_upset_only = 0
# new_upset_only = 0
# both_upset = 0
# for day in days.values():
#     old_upset_only += day["old_upset_only"]
#     new_upset_only += day["new_upset_only"]
#     both_upset += day["both_upset"]
#
# print(f"old_upset_only: {old_upset_only}")
# print(f"new_upset_only: {new_upset_only}")
# print(f"both_upset: {both_upset}")

iterations = 10
season = 13
stats_segment_size = 3
#print_info()
load_all_state(season)
setup_season(season, stats_segment_size)
print_leaders()
