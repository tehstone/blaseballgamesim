from typing import Any, Dict, Tuple
import json
import logging


class TeamState(object):
    def __init__(
        self,
        season: int,
        day: int,
        balls_for_walk: int,
        strikes_for_out: int,
        outs_for_inning: int,
        lineup: Dict[int, str],
        starting_pitcher: str,
        stats: Dict[str, Dict[str, float]],
        blood: Dict[str, str],
    ) -> None:
        """ A container class that holds the team state for a given game """
        self.season = season
        self.day = day
        self.balls_for_walk = balls_for_walk
        self.strikes_for_out = strikes_for_out
        self.outs_for_inning = outs_for_inning
        self.lineup = lineup
        self.starting_pitcher = starting_pitcher
        self.stats = stats
        self.blood = blood

    def to_dict(self) -> Dict[str, Any]:
        """ Gets a dict representation of the state for serialization """
        serialization_dict = {
            "season": self.season,
            "day": self.day,
            "balls_for_walk": self.balls_for_walk,
            "strikes_for_out": self.strikes_for_out,
            "outs_for_inning": self.outs_for_inning,
            "lineup": self.lineup,
            "starting_pitcher": self.starting_pitcher,
            "stats": self.stats,
            "blood": self.blood,
        }
        return serialization_dict

    def save(self, storage_path: str) -> None:
        """ Persist a serialized json of the team state """
        with open(storage_path, "w") as json_file:
            json.dump(self.get_config(), json_file)

    @classmethod
    def load(cls, storage_path: str):
        with open(storage_path, "r") as team_state_file:
            team_state_json = json.load(team_state_file)
            try:
                return TeamState.from_config(team_state_json)
            except KeyError:
                logging.warning(
                    "Unable to load team state file: " + storage_path
                )
                return None

    @classmethod
    def from_config(cls, team_state: Dict[str, Any]):
        """Reconstructs a team state from a json file."""
        season: int = team_state["season"]
        day: int = team_state["day"]
        balls_for_walk: int = team_state["balls_for_walk"]
        strikes_for_out: int = team_state["strikes_for_out"]
        outs_for_inning: int = team_state["outs_for_inning"]
        lineup: Dict[int, str] = team_state["lineup"]
        starting_pitcher: str = team_state["starting_pitcher"]
        stats: Dict[str, Dict[str, float]] = team_state["stats"]
        blood: Dict[str, str] = team_state["blood"]

        return cls(
            season,
            day,
            balls_for_walk,
            strikes_for_out,
            outs_for_inning,
            lineup,
            starting_pitcher,
            stats,
            blood,
        )

    def get_batter_stats_by_position(self, position: int) -> Tuple[str, Dict[str, float]]:
        batter = self.lineup[position]
        stats = self.stats[batter]
        return batter, stats

    def get_player_stats_by_id(self, id: str) -> Dict[str, float]:
        return self.stats[id]
