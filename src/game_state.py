from typing import Any, Dict, List, Optional
from enum import Enum
from joblib import load

import json
import logging
import os
import random

from src.team_state import DEF_ID, TeamState
from src.common import BlaseballStatistics as Stats
from src.common import MachineLearnedModel as Ml
from src.common import BloodType, PitchEventTeamBuff, team_pitch_event_map

CHARM_TRIGGER_PERCENTAGE = 0.02
# TODO(kjc): validate priors for zap and base instincts
ZAP_TRIGGER_PERCENTAGE = 0.02
BASE_INSTINCT_PRIORS = {
    # num bases: map of priors for base to walk to
    4: {
        2: 0.04,
        3: 0.01,
    },
    5: {
        2: 0.035,
        3: 0.01,
        4: 0.005,
    }
}


class InningHalf(Enum):
    TOP = 1
    BOTTOM = 2


class GameState(object):
    def __init__(
        self,
        game_id: str,
        season: int,
        day: int,
        home_team: TeamState,
        away_team: TeamState,
        home_score: int,
        away_score: int,
        inning: int,
        half: InningHalf,
        outs: int,
        strikes: int,
        balls: int,
    ) -> None:
        """ A container class that holds the team state for a given game """
        self.game_id = game_id
        self.season = season
        self.day = day
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.inning = inning
        self.half = half
        self.outs = outs
        self.strikes = strikes
        self.balls = balls
        if self.half == InningHalf.TOP:
            self.cur_batting_team = self.away_team
            self.cur_pitching_team = self.home_team
        else:
            self.cur_batting_team = self.home_team
            self.cur_pitching_team = self.away_team
        # initialize per side variables
        self.num_bases = self.cur_batting_team.num_bases
        self.balls_for_walk = self.cur_batting_team.balls_for_walk
        self.strikes_for_out = self.cur_batting_team.strikes_for_out
        self.outs_for_inning = self.cur_batting_team.outs_for_inning
        self.cur_base_runners: Dict[int, str] = {}
        self.is_game_over = False
        self.clf: Dict[Ml, Any] = {}
        self._load_ml_models()

    def _load_ml_models(self):
        self.clf = {
            Ml.PITCH: load(os.path.join("..", "season_sim", "models", "pitch_v1.joblib")),
            Ml.IS_HIT: load(os.path.join("..", "season_sim", "models", "is_hit_v1.joblib")),
            Ml.HIT_TYPE: load(os.path.join("..", "season_sim", "models", "hit_type_v1.joblib")),
            Ml.RUNNER_ADV_OUT: load(os.path.join("..", "season_sim", "models", "runner_advanced_on_out_v1.joblib")),
            Ml.RUNNER_ADV_HIT: load(os.path.join("..", "season_sim", "models", "extra_base_on_hit_v1.joblib")),
            Ml.SB_ATTEMPT: load(os.path.join("..", "season_sim", "models", "sba_v1.joblib")),
            Ml.SB_SUCCESS: load(os.path.join("..", "season_sim", "models", "sb_success_v1.joblib")),
        }

    def refresh_game_status(self):
        """Refresh game state variables dependant on which team is batting"""
        if self.half == InningHalf.TOP:
            self.cur_batting_team = self.away_team
            self.cur_pitching_team = self.home_team
        else:
            self.cur_batting_team = self.home_team
            self.cur_pitching_team = self.away_team
        self.num_bases = self.cur_batting_team.num_bases
        self.balls_for_walk = self.cur_batting_team.balls_for_walk
        self.strikes_for_out = self.cur_batting_team.strikes_for_out
        self.outs_for_inning = self.cur_batting_team.outs_for_inning

    def reset_inning_counts(self):
        """Reset the counts of an inning"""
        self.reset_pitch_count()
        self.outs = 0

    def reset_pitch_count(self):
        """Reset the pitch count"""
        self.balls = 0
        self.strikes = 0

    def to_dict(self) -> Dict[str, Any]:
        """Gets a dict representation of the state for serialization"""
        serialization_dict = {
            "game_id": self.game_id,
            "season": self.season,
            "day": self.day,
            "num_bases": self.num_bases,
            "inning": self.inning,
            "half": self.half.value,
            "outs": self.outs,
            "strikes": self.strikes,
            "balls": self.balls,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "cur_base_runners": self.cur_base_runners,
            "home_team": self.home_team.to_dict(),
            "away_team": self.away_team.to_dict(),
        }
        return serialization_dict

    def save(self, storage_path: str) -> None:
        """ Persist a serialized json of the team state """
        with open(storage_path, "w") as json_file:
            json.dump(self.to_dict(), json_file)

    @classmethod
    def load(cls, storage_path: str):
        """Load a game state from json"""
        with open(storage_path, "r") as game_state_file:
            game_state_json = json.load(game_state_file)
            try:
                return GameState.from_config(game_state_json)
            except KeyError:
                logging.warning(
                    "Unable to load game state file: " + storage_path
                )
                return None

    @classmethod
    def from_config(cls, game_state: Dict[str, Any]):
        """Reconstructs a team state from a json file."""
        game_id: str = game_state["game_id"]
        season: int = game_state["season"]
        day: int = game_state["day"]
        inning: int = game_state["inning"]
        half: InningHalf = InningHalf(game_state["half"])
        outs: int = game_state["outs"]
        strikes: int = game_state["strikes"]
        balls: int = game_state["balls"]
        home_score: int = game_state["home_score"]
        away_score: int = game_state["away_score"]
        cur_base_runners: Dict[int, str] = game_state["cur_base_runners"]
        home_team: TeamState = TeamState.from_config(game_state["home_team"])
        away_team: TeamState = TeamState.from_config(game_state["away_team"])
        ret_val = cls(
            game_id,
            season,
            day,
            home_team,
            away_team,
            home_score,
            away_score,
            inning,
            half,
            outs,
            strikes,
            balls,
        )
        ret_val.refresh_game_status()
        ret_val.cur_base_runners = cur_base_runners
        return ret_val

    def simulate_game(self) -> None:
        """Loop until the game over state is true"""
        while not self.is_game_over:
            if not self.stolen_base_sim():
                self.pitch_sim()
            self.attempt_to_advance_inning()

    # PITCH MECHANICS
    def pitch_sim(self) -> None:
        """Simulate a pitch with the pre-pitch events and the 4 possible pitch outcomes."""
        if self.resolve_team_pre_pitch_event():
            # A pre-pitch event occurred, skip the pitch and let the game state try to advance
            return
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_PITCHES_THROWN, 1.0)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_PITCHES_FACED, 1.0)
        pitch_fv = self.gen_pitch_fv(
            self.cur_batting_team.get_cur_batter_feature_vector(),
            self.cur_pitching_team.get_pitcher_feature_vector(),
            self.cur_pitching_team.get_defense_feature_vector(),
        )
        pitch_result = self.generic_model_roll(Ml.PITCH, pitch_fv)
        # 0 = ball, 1 = strike, 2 = foul, 3 = in_play
        if pitch_result == 0:
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_BALLS_THROWN, 1.0)
            self.balls += 1
            if self.balls == self.balls_for_walk:
                num_bases_to_advance: int = self.resolve_base_instincts()
                self.resolve_walk(num_bases_to_advance)
            return
        if pitch_result == 1:
            if self.resolve_o_no():
                pitch_result = 2
            else:
                self.cur_pitching_team.update_stat(
                    self.cur_pitching_team.starting_pitcher,
                    Stats.PITCHER_STRIKES_THROWN,
                    1.0
                )
                self.strikes += 1
                if self.strikes == self.strikes_for_out:
                    self.resolve_strikeout()
                return
        if pitch_result == 2:
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_FOUL_BALLS, 1.0)
            if self.strikes < self.strikes_for_out - 1:
                self.strikes += 1
            return
        if pitch_result == 3:
            # Official plate appearance
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_PLATE_APPEARANCES, 1.0)
            self.cur_pitching_team.update_stat(
                self.cur_pitching_team.starting_pitcher,
                Stats.PITCHER_BATTERS_FACED,
                1.0
            )
            self.in_play_sim(pitch_fv)
            self.reset_pitch_count()
            self.cur_batting_team.next_batter()
            return

    def resolve_walk(self, num_bases_to_advance: int) -> None:
        self.advance_all_runners(num_bases_to_advance)
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_WALKS, 1.0)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_WALKS, 1.0)
        self.cur_base_runners[num_bases_to_advance] = self.cur_batting_team.cur_batter
        self.reset_pitch_count()
        self.cur_batting_team.next_batter()

    def resolve_strikeout(self) -> None:
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_STRIKEOUTS, 1.0)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_STRIKEOUTS, 1.0)
        self.outs += 1
        self.reset_pitch_count()
        self.cur_batting_team.next_batter()

    # HIT MECHANICS
    def in_play_sim(self, pitch_feature_vector: List[float]):
        contact_type = self.generic_model_roll(Ml.IS_HIT, pitch_feature_vector)
        # 0 = Flyout, 1 = Groundout, 2 = Hit
        if contact_type == 0:
            self.outs += 1
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_FLYOUTS, 1.0)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_FLYOUTS, 1.0)
            if self.outs < self.outs_for_inning:
                self.attempt_to_advance_runners_on_flyout()
        if contact_type == 1:
            self.outs += 1
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_GROUNDOUTS, 1.0)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_GROUNDOUTS, 1.0)
            if self.outs < self.outs_for_inning:
                self.resolve_fc_dp()
        if contact_type == 2:
            self.hit_sim(pitch_feature_vector)
        self.reset_pitch_count()

    def hit_sim(self, pitch_feature_vector) -> None:
        # lets figure out what kind of hit
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_HITS, 1.0)
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_HITS_ALLOWED, 1.0)
        hit_type = self.generic_model_roll(Ml.HIT_TYPE, pitch_feature_vector)
        # 0 = Single, 1 = Double, 2 = Triple, 3 = HR
        if hit_type == 0:
            self.advance_all_runners(1)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_SINGLES, 1.0)
            self.attempt_to_advance_runners_on_hit()
            self.cur_base_runners[1] = self.cur_batting_team.cur_batter
        if hit_type == 1:
            self.advance_all_runners(2)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_DOUBLES, 1.0)
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_XBH_ALLOWED, 1.0)
            self.attempt_to_advance_runners_on_hit()
            self.cur_base_runners[2] = self.cur_batting_team.cur_batter
        if hit_type == 2:
            self.advance_all_runners(3)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_TRIPLES, 1.0)
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_XBH_ALLOWED, 1.0)
            self.attempt_to_advance_runners_on_hit()
            self.cur_base_runners[3] = self.cur_batting_team.cur_batter
        if hit_type == 3:
            self.advance_all_runners(self.num_bases)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_HRS, 1.0)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_RBIS, 1.0)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_RUNS_SCORED, 1.0)
        self.reset_pitch_count()
        self.cur_batting_team.next_batter()

    def attempt_to_advance_runners_on_hit(self) -> None:
        # TODO(kjc9): implement this logic, for now, never advance
        return

    def attempt_to_advance_runners_on_flyout(self) -> None:
        # TODO(kjc9): implement this logic, for now, never advance
        return

    def resolve_fc_dp(self) -> None:
        # TODO(kjc9): implement this logic, for now, treat it as if everyone advances 1 base
        self.advance_all_runners(1)
        return

    # TEAM BUFF SPECIFIC MECHANICS
    def resolve_team_pre_pitch_event(self) -> bool:
        valid_pre_pitch_pitching_events = [PitchEventTeamBuff.CHARM]
        valid_pre_pitch_batting_events = [PitchEventTeamBuff.ELECTRIC, PitchEventTeamBuff.CHARM]
        if self.cur_pitching_team.team_enum in team_pitch_event_map:
            # Possible event, let's validate
            event, start_season, end_season, req_blood = team_pitch_event_map[self.cur_pitching_team.team_enum]
            # First let's check if a pre-pitch event for the pitcher should trigger
            if team_pitch_event_map[self.cur_pitching_team.team_enum] in valid_pre_pitch_pitching_events:
                # Let's figure out which pitch event it is and deal with it here

                # Deal with charm strikeout chance
                if event == PitchEventTeamBuff.CHARM and self.check_valid_season(start_season, end_season):
                    if self.is_start_of_at_bat() and \
                            self.check_blood_requirement(self.cur_pitching_team.starting_pitcher, req_blood):
                        roll = random.random()
                        if roll < CHARM_TRIGGER_PERCENTAGE:
                            self.resolve_strikeout()
                            return True
                    return False
                # TODO: Add additional pre pitch pitching events here as needed

            # Second, let's check if a pre-pitch event for the batter should trigger
            if team_pitch_event_map[self.cur_batting_team.team_enum] in valid_pre_pitch_batting_events:
                # Let's figure out which batting event it is and deal with it here

                # Deal with charm walk chance
                if event == PitchEventTeamBuff.CHARM and self.check_valid_season(start_season, end_season):
                    if self.is_start_of_at_bat() and \
                            self.check_blood_requirement(self.cur_batting_team.cur_batter, req_blood):
                        roll = random.random()
                        if roll < CHARM_TRIGGER_PERCENTAGE:
                            self.resolve_walk(1)
                            return True
                    return False

                # Deal with zap chance
                if event == PitchEventTeamBuff.ELECTRIC and self.check_valid_season(start_season, end_season):
                    if self.is_start_of_at_bat() and \
                            self.check_blood_requirement(self.cur_batting_team.cur_batter, req_blood):
                        roll = random.random()
                        if roll < ZAP_TRIGGER_PERCENTAGE:
                            self.strikes -= 1
                            return True
                    return False
                # TODO: Add additional pre pitch batting events here as needed

        # Required checks failed, no event triggers
        return False

    def resolve_o_no(self) -> bool:
        if self.cur_batting_team.team_enum in team_pitch_event_map:
            event, start_season, end_season, req_blood = team_pitch_event_map[self.cur_batting_team.team_enum]
            if event == PitchEventTeamBuff.O_NO:
                if self.strikes == 2 and \
                        self.check_valid_season(start_season, end_season) and\
                        self.check_blood_requirement(self.cur_batting_team.cur_batter, req_blood):
                    return True
        return False

    def resolve_base_instincts(self) -> int:
        if self.cur_batting_team.team_enum in team_pitch_event_map:
            event, start_season, end_season, req_blood = team_pitch_event_map[self.cur_batting_team.team_enum]
            if event == PitchEventTeamBuff.BASE_INSTINCTS and \
                    self.check_valid_season(start_season, end_season) and\
                    self.check_blood_requirement(self.cur_batting_team.cur_batter, req_blood):
                roll = random.random()
                cur_base_prior = BASE_INSTINCT_PRIORS[self.cur_batting_team.num_bases]
                total_priors = 0.0
                for num_base in reversed(sorted(cur_base_prior.keys())):
                    total_priors += cur_base_prior[num_base]
                    if roll < total_priors:
                        return num_base
        # Not base instincts team or base instincts did not trigger, only walk one base
        return 1

    def check_blood_requirement(self, player_id: str, blood: BloodType) -> bool:
        if player_id in self.cur_batting_team.blood.keys():
            return self.cur_batting_team.blood[player_id] == blood
        if player_id in self.cur_pitching_team.blood.keys():
            return self.cur_pitching_team.blood[player_id] == blood
        return False

    def check_valid_season(self, start: int, end: Optional[int]) -> bool:
        if self.season >= start:
            if end is None:
                return True
            else:
                return self.season <= end
        return False

    # STOLEN BASE MECHANICS
    def stolen_base_sim(self) -> bool:
        for base in reversed(sorted(self.cur_base_runners.keys())):
            # no one should ever be on home (4 or 5) so this is ok
            next_base = base + 1
            if next_base not in self.cur_base_runners.keys():
                # base is open and available for theft
                base_runner_id = self.cur_base_runners[base]
                base_runner_fv = self.gen_runner_fv(
                    self.cur_batting_team.get_runner_feature_vector(base_runner_id),
                    self.cur_pitching_team.get_defense_feature_vector(),
                    self.cur_pitching_team.get_pitcher_feature_vector(),
                )
                if self.generic_model_roll(Ml.SB_ATTEMPT, base_runner_fv) == 1:
                    self.cur_batting_team.update_stat(base_runner_id, Stats.STOLEN_BASE_ATTEMPT, 1.0)
                    self.cur_pitching_team.update_stat(DEF_ID, Stats.DEFENSE_STOLEN_BASE_ATTEMPTS, 1.0)
                    self.cur_pitching_team.update_stat(
                        self.cur_pitching_team.starting_pitcher,
                        Stats.DEFENSE_STOLEN_BASE_ATTEMPTS,
                        1.0
                    )
                    if self.generic_model_roll(Ml.SB_SUCCESS, base_runner_fv) == 1:
                        self.cur_batting_team.update_stat(base_runner_id, Stats.STOLEN_BASE, 1.0)
                        self.cur_pitching_team.update_stat(DEF_ID, Stats.DEFENSE_STOLEN_BASE, 1.0)
                        self.cur_pitching_team.update_stat(
                            self.cur_pitching_team.starting_pitcher,
                            Stats.DEFENSE_STOLEN_BASE,
                            1.0
                        )
                        self.update_base_runner(base, Stats.STOLEN_BASE)
                    else:
                        self.cur_batting_team.update_stat(base_runner_id, Stats.CAUGHT_STEALINGS, 1.0)
                        self.cur_pitching_team.update_stat(DEF_ID, Stats.DEFENSE_CAUGHT_STEALINGS, 1.0)
                        self.cur_pitching_team.update_stat(
                            self.cur_pitching_team.starting_pitcher,
                            Stats.DEFENSE_CAUGHT_STEALINGS,
                            1.0
                        )
                        self.update_base_runner(base, Stats.CAUGHT_STEALINGS)
                    # runner attempted to steal
                    return True
        # No steal attempt was made by any runner
        return False

    # BASE RUNNING MECHANICS
    def advance_all_runners(self, num_bases_to_advance: int) -> None:
        for base in reversed(sorted(self.cur_base_runners.keys())):
            self.update_base_runner(base, Stats.WALK_ADVANCEMENT, num_bases_to_advance)

    def update_base_runner(self, base: int, action: Stats, num_bases_to_advance: int = 1) -> None:
        if action == Stats.CAUGHT_STEALINGS:
            self.outs += 1
            del self.cur_base_runners[base]
            return
        if action == Stats.STOLEN_BASES:
            # Can only steal 1 base at a time so no variable here
            if base == self.num_bases - 1:
                # run scores
                self.cur_pitching_team.update_stat(
                    self.cur_pitching_team.starting_pitcher,
                    Stats.PITCHER_EARNED_RUNS,
                    1.0
                )
                self.increase_batting_team_runs(1)
                del self.cur_base_runners[base]
            else:
                new_base = base + 1
                assert new_base not in self.cur_base_runners
                assert new_base < self.num_bases
                runner_id = self.cur_base_runners[base]
                self.cur_base_runners[new_base] = runner_id
                del self.cur_base_runners[base]
            return
        if action == Stats.WALK_ADVANCEMENT:
            if base > self.num_bases - num_bases_to_advance:
                # run scores
                self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_RBIS, 1.0)
                self.cur_batting_team.update_stat(self.cur_base_runners[base], Stats.BATTER_RUNS_SCORED, 1.0)
                self.cur_pitching_team.update_stat(
                    self.cur_pitching_team.starting_pitcher,
                    Stats.PITCHER_EARNED_RUNS,
                    1.0
                )
                self.increase_batting_team_runs(1)
                del self.cur_base_runners[base]
            else:
                new_base = base + num_bases_to_advance
                assert new_base not in self.cur_base_runners
                assert new_base < self.num_bases
                runner_id = self.cur_base_runners[base]
                self.cur_base_runners[new_base] = runner_id
                del self.cur_base_runners[base]
            return

    # GENERIC HELPER METHODS
    def is_start_of_at_bat(self) -> bool:
        return self.balls == 0 and self.strikes == 0

    def generic_model_roll(self, model: Ml, feature_vector: List[float]) -> int:
        probs: List[float] = self.clf[model].predict_proba(feature_vector)
        # generate random float between 0-1
        roll = random.random()
        total = 0
        for i in range(len(probs)):
            # add the odds of the next outcome to the running total
            total += probs[i]
            # if the random roll is less than the new total, return this outcome
            if roll < total:
                return i

    def increase_batting_team_runs(self, amt: int) -> None:
        if self.half == InningHalf.TOP:
            self.away_score += amt
        else:
            self.home_score += amt

    def attempt_to_advance_inning(self) -> None:
        if self.inning < 9:
            # Game can never be over here.  Advance normally.
            if self.outs == self.outs_for_inning:
                # Team has reached their max number of outs
                self.cur_base_runners = {}
                if self.half == InningHalf.TOP:
                    self.half = InningHalf.BOTTOM
                else:
                    self.inning += 1
                    self.half = InningHalf.TOP
                self.refresh_game_status()
                self.reset_inning_counts()
        else:
            # Game can now be over when advancing, must check state
            if self.outs == self.outs_for_inning:
                if self.half == InningHalf.TOP:
                    if self.home_score > self.away_score:
                        self.is_game_over = True
                    else:
                        self.half = InningHalf.BOTTOM
                        self.refresh_game_status()
                        self.reset_inning_counts()
                if self.half == InningHalf.BOTTOM:
                    if self.home_score != self.away_score:
                        self.is_game_over = True
                    else:
                        self.half = InningHalf.TOP
                        self.inning += 1
                        self.refresh_game_status()
                        self.reset_inning_counts()

    @classmethod
    def gen_runner_fv(
            cls,
            runner_stlats: List[float],
            defense_stlats: List[float],
            pitcher_stlats: List[float]
    ) -> List[float]:
        ret_val = runner_stlats
        ret_val.extend(defense_stlats)
        ret_val.extend(pitcher_stlats)
        return ret_val

    @classmethod
    def gen_pitch_fv(
            cls,
            batter_stlats: List[float],
            pitcher_stlats: List[float],
            defense_stlats: List[float],
    ) -> List[float]:
        ret_val = batter_stlats
        ret_val.extend(pitcher_stlats)
        ret_val.extend(defense_stlats)
        return ret_val
