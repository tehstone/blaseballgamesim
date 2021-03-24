import json
import os
from typing import Dict, Any

from src.common import blood_id_map, fk_key, blood_name_map, Team, team_id_map, Weather, get_player_stlats
from src.game_state import GameState, InningHalf
from src.team_state import DEF_ID, TeamState
from src.common import ForbiddenKnowledge as FK
from src.common import BlaseballStatistics as Stats, team_name_map

team_states: Dict[Team, TeamState] = {}

def get_stlat_dict(player: Dict[str, Any]) -> Dict[FK, float]:
    ret_val: Dict[FK, float] = {}
    for k in fk_key:
        str_name = fk_key[k]
        ret_val[k] = float(player[str_name])
    return ret_val


def load_state(team_info, team_id, season, day):
    player_stlats_list = get_player_stlats(season, day)
    for player in player_stlats_list:
        if day == 6 and player["team_id"] == "105bc3ff-1320-4e37-8ef0-8d595cb95dd0":
            x = 1
        if player["team_id"] != team_id:
            continue
        player_id = player["player_id"]
        pos = int(player["position_id"]) + 1
        if "position_type_id" in player:
            if player["position_type_id"] == "0":
                team_info[team_id]["lineup"][pos] = player_id
            else:
                team_info[team_id]["rotation"][pos] = player_id
        else:
            if player["position_type"] == "BATTER":
                team_info[team_id]["lineup"][pos] = player_id
            else:
                team_info[team_id]["rotation"][pos] = player_id
        team_info[team_id]["stlats"][player_id] = get_stlat_dict(player)

        team_info[team_id]["game_stats"][player_id] = {}
        team_info[team_id]["game_stats"][DEF_ID] = {}

        team_info[team_id]["names"][player_id] = player["player_name"]

        try:
            team_info[team_id]["blood"][player_id] = blood_id_map[int(player["blood"])]
        except ValueError:
            team_info[team_id]["blood"][player_id] = blood_name_map[player["blood"]]
    return team_info

# s7 d1 crabs
home_team = "8d87c468-699a-47a8-b40d-cfb73a5660ad"
h_team_pitcher = "3af96a6b-866c-4b03-bc14-090acf6ecee5"
#s14 d99 tigers
away_team = "747b8e4a-7e50-4638-a973-ea7950a3e739"
a_team_pitcher = "2720559e-9173-4042-aaa0-d3852b72ab2e"
h_team_season = 6
a_team_season = 13
h_team_day = 0
a_team_day = 98

team_info = {
    home_team: {
        "lineup": {},
        "rotation": {},
        "blood": {},
        "game_stats": {},
        "stlats": {},
        "names": {}
    },
    away_team: {
        "lineup": {},
        "rotation": {},
        "blood": {},
        "game_stats": {},
        "stlats": {},
        "names": {}
    }
}

load_state(team_info, home_team, h_team_season, h_team_day)
load_state(team_info, away_team, a_team_season, a_team_day)

home_team_state = TeamState(
            team_id=home_team,
            season=h_team_season,
            day=h_team_season,
            weather=Weather.SUN2,
            is_home=True,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup=team_info[home_team]["lineup"],
            rotation=team_info[home_team]["rotation"],
            starting_pitcher=h_team_pitcher,
            stlats=team_info[home_team]["stlats"],
            game_stats=team_info[home_team]["game_stats"],
            blood=team_info[home_team]["blood"],
            player_names=team_info[home_team]["names"],
            cur_batter_pos=1,
        )

away_team_state = TeamState(
            team_id=away_team,
            season=a_team_season,
            day=a_team_season,
            weather=Weather.SUN2,
            is_home=True,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup=team_info[away_team]["lineup"],
            rotation=team_info[away_team]["rotation"],
            starting_pitcher=a_team_pitcher,
            stlats=team_info[away_team]["stlats"],
            game_stats=team_info[away_team]["game_stats"],
            blood=team_info[away_team]["blood"],
            player_names=team_info[away_team]["names"],
            cur_batter_pos=1,
        )

game = GameState(
                game_id="1",
                season=0,
                day=0,
                home_team=home_team_state,
                away_team=away_team_state,
                home_score=0,
                away_score=0,
                inning=1,
                half=InningHalf.TOP,
                outs=0,
                strikes=0,
                balls=0,
                weather=Weather.SUN2
            )
iterations = 250
for x in range(0, iterations):
    game.simulate_game()
    game.reset_game_state()

home_win_count = home_team_state.game_stats[DEF_ID][Stats.TEAM_WINS]
print(f"{team_name_map[home_team_state.team_enum]} win: {home_win_count} "
      f"({home_win_count / iterations})")
