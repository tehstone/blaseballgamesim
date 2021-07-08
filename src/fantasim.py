from decimal import Decimal
from typing import Dict, Any

from common import blood_id_map, fk_key, blood_name_map, Team, Weather, BloodType
from game_state import GameState, InningHalf
from stadium import Stadium
from team_state import DEF_ID, TeamState
from common import ForbiddenKnowledge as FK

default_stadium = Stadium(
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

team_states: Dict[Team, TeamState] = {}

def get_stlat_dict(player: Dict[str, Any]) -> Dict[FK, float]:
    ret_val: Dict[FK, float] = {}
    for k in fk_key:
        str_name = fk_key[k]
        ret_val[k] = float(player[str_name])
    return ret_val


def load_state(team):
    team_info = {
        "name": team["name"],
        "lineup": {},
        "rotation": {},
        "blood": {},
        "game_stats": {},
        "segmented_stats": {},
        "stlats": {},
        "buffs": {},
        "names": {}
    }
    l_pos = 1
    for player in team["lineup"]:
        player_id = player["id"]
        team_info["lineup"][l_pos] = player_id
        l_pos += 1
        team_info["stlats"][player_id] = get_stlat_dict(player)

        team_info["game_stats"][player_id] = {}
        team_info["game_stats"][DEF_ID] = {}
        team_info["names"][player_id] = player["name"]

        team_info["buffs"][player_id] = {}

        try:
            team_info["blood"][player_id] = blood_id_map[int(player["blood"])]
        except ValueError:
            team_info["blood"][player_id] = blood_name_map[player["blood"]]
        except TypeError:
            team_info["blood"][player_id] = BloodType.A
    r_pos = 1
    for player in team["rotation"]:
        player_id = player["id"]
        team_info["rotation"][r_pos] = player_id
        r_pos += 1
        team_info["stlats"][player_id] = get_stlat_dict(player)

        team_info["game_stats"][player_id] = {}
        team_info["game_stats"][DEF_ID] = {}
        team_info["names"][player_id] = player["name"]

        team_info["buffs"][player_id] = {}

        try:
            team_info["blood"][player_id] = blood_id_map[int(player["blood"])]
        except ValueError:
            team_info["blood"][player_id] = blood_name_map[player["blood"]]
        except TypeError:
            team_info["blood"][player_id] = BloodType.A
    return team_info


def setup_and_run_custom(team_dict):
    home_team = team_dict["home_team"]["id"]
    away_team = team_dict["away_team"]["id"]
    season, day = 0, 0

    team_info = load_state(team_dict["home_team"])
    home_team_state = TeamState(
                team_id=home_team,
                name=team_info["name"],
                season=season,
                day=day,
                stadium=default_stadium,
                weather=Weather.SUN2,
                is_home=True,
                num_bases=4,
                balls_for_walk=4,
                strikes_for_out=3,
                outs_for_inning=3,
                lineup=team_info["lineup"],
                rotation=team_info["rotation"],
                starting_pitcher=team_info["rotation"][1],
                cur_pitcher_pos=1,
                stlats=team_info["stlats"],
                buffs=team_info["buffs"],
                game_stats=team_info["game_stats"],
                segmented_stats=team_info["segmented_stats"],
                blood=team_info["blood"],
                player_names=team_info["names"],
                cur_batter_pos=1,
                segment_size=1,
            )

    team_info = load_state(team_dict["away_team"])
    away_team_state = TeamState(
                team_id=away_team,
                name=team_info["name"],
                season=season,
                day=day,
                stadium=default_stadium,
                weather=Weather.SUN2,
                is_home=True,
                num_bases=4,
                balls_for_walk=4,
                strikes_for_out=3,
                outs_for_inning=3,
                lineup=team_info["lineup"],
                rotation=team_info["rotation"],
                starting_pitcher=team_info["rotation"][1],
                cur_pitcher_pos=1,
                stlats=team_info["stlats"],
                buffs=team_info["buffs"],
                game_stats=team_info["game_stats"],
                segmented_stats=team_info["segmented_stats"],
                blood=team_info["blood"],
                player_names=team_info["names"],
                cur_batter_pos=1,
                segment_size=1,
            )

    game = GameState(
                    game_id="1",
                    season=0,
                    day=0,
                    stadium=default_stadium,
                    home_team=home_team_state,
                    away_team=away_team_state,
                    home_score=Decimal("0"),
                    away_score=Decimal("0"),
                    inning=1,
                    half=InningHalf.TOP,
                    outs=0,
                    strikes=0,
                    balls=0,
                    weather=Weather.SUN2
                )

    home_score, away_score, event_log = game.simulate_game()

    return float(home_score), float(away_score), event_log

