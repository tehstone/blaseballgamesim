def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from joblib import load

import json
import logging
import os
import random

from team_state import DEF_ID, TEAM_ID, TeamState
from common import BlaseballStatistics as Stats
from common import MachineLearnedModel as Ml
from common import BloodType, PitchEventTeamBuff, PlayerBuff, pitch_reroll_event_map, team_pitch_event_map, Weather
from common import season_based_event_map, SeasonEventTeamBuff
from stadium import Stadium


class Eval(object):
    def __init__(
        self,
        home_team: TeamState,
        away_team: TeamState,
        strikes: int,
        balls: int,
    ) -> None:
        """ A container class that holds the team state for a given game """
        self.day = 1
        self.home_team = home_team
        self.away_team = away_team
        self.strikes = strikes
        self.balls = balls
        self.cur_batting_team = self.away_team
        self.cur_pitching_team = self.home_team

        # initialize per side variables
        self.num_bases = self.cur_batting_team.num_bases
        self.balls_for_walk = self.cur_batting_team.balls_for_walk
        self.strikes_for_out = self.cur_batting_team.strikes_for_out
        self.outs_for_inning = self.cur_batting_team.outs_for_inning
        self.cur_base_runners: Dict[int, str] = {}
        self.is_game_over = False
        self.clf: Dict[Ml, Any] = {}
        self.game_log: List[str] = ["Play ball."]
        self.refresh_game_status()
        self._load_ml_models()

    def _load_ml_models(self):
        self.clf = {
            Ml.PITCH: load(os.path.join("..", "season_sim", "models", "pitch_v22.joblib")),
            Ml.HIT_TYPE: load(os.path.join("..", "season_sim", "models", "hit_type_v22.joblib")),
            Ml.OUT_TYPE: load(os.path.join("..", "season_sim", "models", "out_type_v22.joblib")),
        }

    def log_event(self, event: str) -> None:
        self.game_log.append(event)

    def reset_game_state(self, game_stats_reset=False) -> None:
        """Reset the game state to the start of the game"""
        self.refresh_game_status()
        self.home_team.reset_team_state(game_stats_reset)
        self.away_team.reset_team_state(game_stats_reset)
        self.game_log = ["Play ball."]
        self.is_game_over = False
        self.refresh_game_status()

    def refresh_game_status(self):
        """Refresh game state variables dependant on which team is batting"""
        self.num_bases = self.cur_batting_team.num_bases
        self.balls_for_walk = self.cur_batting_team.balls_for_walk
        self.strikes_for_out = self.cur_batting_team.strikes_for_out
        self.outs_for_inning = self.cur_batting_team.outs_for_inning

    def reset_pitch_count(self):
        """Reset the pitch count"""
        self.balls = 0
        self.strikes = 0

    def simulate_game(self) -> None:
        """Loop until the game over state is true"""
        pitcher_count = 1
        while pitcher_count <= 2:
            while not self.is_game_over:
                if self.cur_batting_team.cur_batter in self.cur_batting_team.game_stats:
                    if Stats.BATTER_PLATE_APPEARANCES in self.cur_batting_team.game_stats[self.cur_batting_team.cur_batter]:
                        if self.cur_batting_team.game_stats[self.cur_batting_team.cur_batter][Stats.BATTER_PLATE_APPEARANCES] == 100:
                            self.is_game_over = True
                self.pitch_sim()
            self.cur_batting_team.reset_team_state(game_stat_reset=True, lineup_changed=False)
            self.is_game_over = False
            self.cur_pitching_team.next_pitcher()
            pitcher_count = pitcher_count + 1
        return

    def validate_current_batter_state(self):
        cur_buffs = self.cur_batting_team.player_buffs[self.cur_batting_team.cur_batter]
        if PlayerBuff.ELSEWHERE in cur_buffs.keys() or PlayerBuff.SHELLED in cur_buffs.keys():
            self.log_event(f"Skipping {self.cur_batting_team.get_cur_batter_name()} due to UNAVAILABILITY.")
            self.cur_batting_team.next_batter()
            self.validate_current_batter_state()

    # PITCH MECHANICS
    def pitch_sim(self) -> None:
        """Simulate a pitch with the pre-pitch events and the 4 possible pitch outcomes."""
        self.validate_current_batter_state()
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                           Stats.PITCHER_PITCHES_THROWN, 1.0, self.day)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                          Stats.BATTER_PITCHES_FACED, 1.0, self.day)
        pitch_fv = self.gen_pitch_fv(
            self.cur_batting_team.get_cur_batter_feature_vector(),
            self.cur_pitching_team.get_pitcher_feature_vector(),
            [0.773526430988913, 0.826184892943561, 0.7901157143783870, 0.8133712472630720, 0.7665729800544850, 0.0],
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0]
        )
        pitch_result = self.generic_model_roll(Ml.PITCH, pitch_fv)

        num_strikes = 1

        # 0 = ball, 1 = strike_swinging, 2 = foul, 3 = in_play_hit, 4 = in_play_out, 5 = strike_looking
        if pitch_result == 0:
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                               Stats.PITCHER_BALLS_THROWN, 1.0, self.day)
            self.balls += 1
            self.log_event(f'Ball {self.balls}.')
            if self.balls == self.balls_for_walk:
                num_bases_to_advance: int = 1
                self.resolve_walk(num_bases_to_advance)
            return
        if pitch_result == 1:
            self.cur_pitching_team.update_stat(
                self.cur_pitching_team.starting_pitcher,
                Stats.PITCHER_STRIKES_THROWN,
                float(num_strikes),
                self.day
            )
            self.strikes += num_strikes
            self.log_event(f'Strike swinging. Strike {self.strikes}.')
            if self.strikes >= self.strikes_for_out:
                self.resolve_strikeout()
            return
        if pitch_result == 5:
            self.cur_pitching_team.update_stat(
                self.cur_pitching_team.starting_pitcher,
                Stats.PITCHER_STRIKES_THROWN,
                float(num_strikes),
                self.day
            )
            self.strikes += num_strikes
            self.log_event(f'Strike looking. Strike {self.strikes}.')
            if self.strikes >= self.strikes_for_out:
                self.resolve_strikeout()
            return
        if pitch_result == 2:
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_FOUL_BALLS, 1.0, self.day)
            if self.strikes < self.strikes_for_out - 1:
                self.strikes += 1
                self.log_event(f'Foul ball.  Strike {self.strikes}.')
            else:
                self.log_event(f'Foul ball.')
            return
        if pitch_result == 3:
            # Its a hit
            # Official plate appearance
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_PLATE_APPEARANCES, 1.0, self.day)
            self.cur_pitching_team.update_stat(
                self.cur_pitching_team.starting_pitcher,
                Stats.PITCHER_BATTERS_FACED,
                1.0,
                self.day
            )
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_AT_BATS, 1.0, self.day)
            self.hit_sim(pitch_fv)
            self.cur_batting_team.apply_hit_to_buffs(self.cur_batting_team.cur_batter)
            self.reset_pitch_count()
            self.cur_batting_team.next_batter()
            self.log_event(f'{self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} now at bat.')
            return
        if pitch_result == 4:
            # Its an out
            # Official plate appearance
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_PLATE_APPEARANCES, 1.0, self.day)
            self.cur_pitching_team.update_stat(
                self.cur_pitching_team.starting_pitcher,
                Stats.PITCHER_BATTERS_FACED,
                1.0,
                self.day
            )
            self.in_play_sim(pitch_fv)
            self.reset_pitch_count()
            self.cur_batting_team.next_batter()
            self.log_event(f'{self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} now at bat.')
            return

    def resolve_walk(self, num_bases_to_advance: int) -> None:
        self.log_event(f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} walks to base {num_bases_to_advance}.')
        # advance runners that are able
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher, Stats.PITCHER_WALKS, 1.0, self.day)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter, Stats.BATTER_WALKS, 1.0, self.day)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                          Stats.BATTER_PLATE_APPEARANCES, 1.0, self.day)
        self.cur_pitching_team.update_stat(
            self.cur_pitching_team.starting_pitcher,
            Stats.PITCHER_BATTERS_FACED,
            1.0,
            self.day
        )

        self.reset_pitch_count()
        self.cur_batting_team.next_batter()
        self.log_event(f'{self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} now at bat.')

    def resolve_strikeout(self) -> None:
        self.log_event(f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} strikes out.')
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                           Stats.PITCHER_STRIKEOUTS, 1.0, self.day)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                          Stats.BATTER_STRIKEOUTS, 1.0, self.day)
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                          Stats.BATTER_PLATE_APPEARANCES, 1.0, self.day)
        self.cur_pitching_team.update_stat(
            self.cur_pitching_team.starting_pitcher,
            Stats.PITCHER_BATTERS_FACED,
            1.0,
            self.day
        )

        self.reset_pitch_count()
        self.cur_batting_team.next_batter()
        self.log_event(f'{self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} now at bat.')

    # HIT MECHANICS
    def in_play_sim(self, pitch_feature_vector: List[List[float]], acidic_pitcher_check: bool = False) -> None:
        contact_type = self.generic_model_roll(Ml.OUT_TYPE, pitch_feature_vector)
        # 0 = Flyout, 1 = Groundout
        if contact_type == 0:
            self.log_event(
                f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} flies out.')
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                               Stats.PITCHER_FLYOUTS, 1.0, self.day)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_FLYOUTS, 1.0, self.day)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_AT_BATS, 1.0, self.day)
        if contact_type == 1:
            self.log_event(
                f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} grounds out.')
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                               Stats.PITCHER_GROUNDOUTS, 1.0, self.day)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_GROUNDOUTS, 1.0, self.day)
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_AT_BATS, 1.0, self.day)
        self.reset_pitch_count()

    def hit_sim(self, pitch_feature_vector) -> None:
        # lets figure out what kind of hit
        self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                          Stats.BATTER_HITS, 1.0, self.day)
        self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                           Stats.PITCHER_HITS_ALLOWED, 1.0, self.day)
        hit_type = self.generic_model_roll(Ml.HIT_TYPE, pitch_feature_vector)
        # 0 = Single, 1 = Double, 2 = Triple, 3 = HR
        if hit_type == 0:
            self.log_event(
                f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} hits a single.')
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_SINGLES, 1.0, self.day)
        if hit_type == 1:
            self.log_event(
                f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} hits a double.')
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_DOUBLES, 1.0, self.day)
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                               Stats.PITCHER_XBH_ALLOWED, 1.0, self.day)
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                               Stats.PITCHER_DOUBLE_ALLOWED, 1.0, self.day)
        if hit_type == 2:
            self.log_event(
                f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} hits a triple.')
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_TRIPLES, 1.0, self.day)
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                           Stats.PITCHER_XBH_ALLOWED, 1.0, self.day)
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                           Stats.PITCHER_TRIPLE_ALLOWED, 1.0, self.day)
        if hit_type == 3:
            self.log_event(
                f'Batter {self.cur_batting_team.get_player_name(self.cur_batting_team.cur_batter)} hits a home run.')
            self.cur_batting_team.update_stat(self.cur_batting_team.cur_batter,
                                              Stats.BATTER_HRS, 1.0, self.day)
            # batter scores
            self.cur_pitching_team.update_stat(self.cur_pitching_team.starting_pitcher,
                                               Stats.PITCHER_HRS_ALLOWED, 1.0, self.day)

        self.reset_pitch_count()

    def _random_roll(self) -> float:
        return random.random()

    # GENERIC HELPER METHODS
    def is_start_of_at_bat(self) -> bool:
        return self.balls == 0 and self.strikes == 0

    def generic_model_roll(self, model: Ml, feature_vector: List[List[float]]) -> int:
        probs: List[float] = self.clf[model].predict_proba(feature_vector)[0]
        # generate random float between 0-1
        roll = self._random_roll()
        total = 0.0
        for i in range(len(probs)):
            # add the odds of the next outcome to the running total
            total += probs[i]
            # if the random roll is less than the new total, return this outcome
            if roll < total:
                return i

    @classmethod
    def gen_pitch_fv(
            cls,
            batter_stlats: List[float],
            pitcher_stlats: List[float],
            defense_stlats: List[float],
            stadium_stlats: List[float],
    ) -> List[List[float]]:
        ret_val = batter_stlats
        ret_val.extend(pitcher_stlats)
        ret_val.extend(defense_stlats)
        ret_val.extend(stadium_stlats)
        return [ret_val]
