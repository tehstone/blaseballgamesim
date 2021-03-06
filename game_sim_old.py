import asyncio
import json
import os
import random

import requests
import statistics

from joblib import load
from requests import Timeout

team_names = {
"b72f3061-f573-40d7-832a-5ad475bd7909": "Lovers",
"878c1bf6-0d21-4659-bfee-916c8314d69c": "Tacos",
"b024e975-1c4a-4575-8936-a3754a08806a": "Steaks",
"adc5b394-8f76-416d-9ce9-813706877b84": "Breath Mints",
"ca3f1c8c-c025-4d8e-8eef-5be6accbeb16": "Firefighters",
"bfd38797-8404-4b38-8b82-341da28b1f83": "Shoe Thieves",
"3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e": "Flowers",
"979aee4a-6d80-4863-bf1c-ee1a78e06024": "Fridays",
"7966eb04-efcc-499b-8f03-d13916330531": "Magic",
"36569151-a2fb-43c1-9df7-2df512424c82": "Millennials",
"8d87c468-699a-47a8-b40d-cfb73a5660ad": "Crabs",
"9debc64f-74b7-4ae1-a4d6-fce0144b6ea5": "Spies",
"23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7": "Pies",
"f02aeae2-5e6a-4098-9842-02d2273f25c7": "Sunbeams",
"57ec08cc-0411-4643-b304-0e80dbc15ac7": "Wild Wings",
"747b8e4a-7e50-4638-a973-ea7950a3e739": "Tigers",
"eb67ae5e-c4bf-46ca-bbbc-425cd34182ff": "Moist Talkers",
"b63be8c2-576a-4d6e-8daf-814f8bcea96f": "Dale",
"105bc3ff-1320-4e37-8ef0-8d595cb95dd0": "Garages",
"a37f9158-7f82-46bc-908c-c9e2dda7c33b": "Jazz Hands",
"c73b705c-40ad-4633-a6ed-d357ee2e2bcf": "Lift"
}
team_effects = {"3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e": {"growth": 8}}
blood_effect = {"f02aeae2-5e6a-4098-9842-02d2273f25c7": {"base_instincts": {"season": 8, "blood": 4}}}
base_instincts_procs = {8: {2: 0, 3: 0}, 9: {2: 0, 3: 0}, 10: {2: 0, 3: 0}}
stlat_list = ["anticapitalism", "chasiness", "omniscience", "tenaciousness", "watchfulness", "pressurization",
              "cinnamon", "buoyancy", "divinity", "martyrdom", "moxie", "musclitude", "patheticism", "thwackability",
              "tragicness", "base_thirst", "continuation", "ground_friction", "indulgence", "laserlikeness",
              "coldness", "overpowerment", "ruthlessness", "shakespearianism", "suppression", "unthwackability"]

async def retry_request(url, tries=10):
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
            await asyncio.sleep(.5)
    return None


def apply_effect(def_stlats, effect, day):
    if effect == "growth":
        def_stlats = {k: float(v) * (1.0 + (day / 99 * 0.05)) for (k, v) in def_stlats.items() if k in stlat_list}
    return def_stlats


def apply_effect_deep(def_stlats, effect, day):
    if effect == "growth":
        for key, stlats in def_stlats.items():
            def_stlats[key] = {k: float(v) * (1.0 + (day / 99 * 0.05)) for (k, v) in stlats.items() if k in stlat_list}
    return def_stlats


async def setup_models(games, clf, player_stlats, team_stlats):
    hitter_models = {}
    for game in games:
        if game["homePitcher"] not in player_stlats:
            continue
        if game["awayPitcher"] not in player_stlats:
            continue
        home_pitcher = player_stlats[game["homePitcher"]]
        away_pitcher = player_stlats[game["awayPitcher"]]
        home_hitters = home_defense = team_stlats[game['homeTeam']]["lineup"]
        away_hitters = away_defense = team_stlats[game['awayTeam']]["lineup"]
        if game["homeTeam"] in team_effects:
            for effect, start_season in team_effects[game["homeTeam"]].items():
                if game["season"] >= start_season:
                    home_defense = apply_effect_deep(home_defense, effect, game["day"])
                    home_hitters = apply_effect_deep(home_hitters, effect, game["day"])
                    home_pitcher = apply_effect(home_pitcher, effect, game["day"])
        if game["awayTeam"] in team_effects:
            for effect, start_season in team_effects[game["awayTeam"]].items():
                if game["season"] >= start_season:
                    away_defense = apply_effect_deep(away_defense, effect, game["day"])
                    away_hitters = apply_effect_deep(away_hitters, effect, game["day"])
                    away_pitcher = apply_effect(away_pitcher, effect, game["day"])
        h_anticapitalism = statistics.mean([float(d["anticapitalism"]) for d in home_defense.values()])
        h_chasiness = statistics.mean([float(d["chasiness"]) for d in home_defense.values()])
        h_omniscience = statistics.mean([float(d["omniscience"]) for d in home_defense.values()])
        h_tenaciousness = statistics.mean([float(d["tenaciousness"]) for d in home_defense.values()])
        h_watchfulness = statistics.mean([float(d["watchfulness"]) for d in home_defense.values()])
        h_defense_pressurization = statistics.mean([float(d["pressurization"]) for d in home_defense.values()])
        h_defense_cinnamon = statistics.mean([float(d["cinnamon"]) for d in home_defense.values()])
        a_anticapitalism = statistics.mean([float(d["anticapitalism"]) for d in away_defense.values()])
        a_chasiness = statistics.mean([float(d["chasiness"]) for d in away_defense.values()])
        a_omniscience = statistics.mean([float(d["omniscience"]) for d in away_defense.values()])
        a_tenaciousness = statistics.mean([float(d["tenaciousness"]) for d in away_defense.values()])
        a_watchfulness = statistics.mean([float(d["watchfulness"]) for d in away_defense.values()])
        a_defense_pressurization = statistics.mean([float(d["pressurization"]) for d in away_defense.values()])
        a_defense_cinnamon = statistics.mean([float(d["cinnamon"]) for d in away_defense.values()])
        model_arrs = []
        sorted_h_hitters = {k: v for k, v in
                            sorted(home_hitters.items(), key=lambda item: item[0])}
        sorted_a_hitters = {k: v for k, v in
                            sorted(away_hitters.items(), key=lambda item: item[0])}
        for __, hitter in sorted_h_hitters.items():
            m_arr = []
            for stlat in ["buoyancy", "divinity", "martyrdom", "moxie", "musclitude", "patheticism",
                          "thwackability", "tragicness", "base_thirst", "continuation",
                          "ground_friction", "indulgence", "laserlikeness", "cinnamon", "pressurization"]:
                m_arr.append(float(hitter[stlat]))
            for stlat in ["coldness", "overpowerment", "ruthlessness", "shakespearianism",
                          "suppression", "unthwackability", "cinnamon", "pressurization"]:
                m_arr.append(float(away_pitcher[stlat]))
            m_arr += [a_anticapitalism, a_chasiness, a_omniscience, a_tenaciousness,
                      a_watchfulness, a_defense_pressurization, a_defense_cinnamon]
            model_arrs.append(m_arr)
        for __, hitter in sorted_a_hitters.items():
            m_arr = []
            for stlat in ["buoyancy", "divinity", "martyrdom", "moxie", "musclitude", "patheticism",
                          "thwackability", "tragicness", "base_thirst", "continuation",
                          "ground_friction", "indulgence", "laserlikeness", "cinnamon", "pressurization"]:
                m_arr.append(float(hitter[stlat]))
            for stlat in ["coldness", "overpowerment", "ruthlessness", "shakespearianism",
                          "suppression", "unthwackability", "cinnamon", "pressurization"]:
                m_arr.append(float(home_pitcher[stlat]))
            m_arr += [h_anticapitalism, h_chasiness, h_omniscience, h_tenaciousness,
                      h_watchfulness, h_defense_pressurization, h_defense_cinnamon]
            hit_model_arrs.append(m_arr)
        probs = clf.predict_proba(hit_model_arrs)
        counter = 0
        for hitter, __ in sorted_h_hitters.items():
            hitter_models[hitter] = probs[counter]
            counter += 1
        for hitter, __ in sorted_a_hitters.items():
            hitter_models[hitter] = probs[counter]
            counter += 1

    return hitter_models


async def simulate(games, model, team_stlats, player_blood_types, player_names, sim_length):
    a_favored_wins, p_favored_wins, predicted_wins = 0, 0, 0
    day = games[0]['day']
    season = games[0]['season']
    output_text = f"Day: {day}\n"
    strikeouts = {}
    game_statsheets = {}
    for game in games:
        home_scores = []
        away_scores = []
        home_shutout = 0
        home_wins = 0
        away_shutout = 0
        away_wins = 0
        home_struckout = []
        away_struckout = []
        innings = []
        homeTeam, awayTeam = game["homeTeam"], game["awayTeam"]
        home_name = team_names[homeTeam]
        away_name = team_names[awayTeam]
        home_lineup = team_stlats[homeTeam]["lineup"]
        away_lineup = team_stlats[awayTeam]["lineup"]
        for hitter in list(home_lineup.keys()) + list(away_lineup.keys()):
            game_statsheets[hitter] = {"plate_appearances": 0, "at_bats": 0, "struckouts": 0, "walks": 0,
                                       "hits": 0, "doubles": 0, "triples": 0, "quadruples": 0, "homeruns": 0,
                                       "runs": 0, "rbis": 0, "stolen_bases": 0,
                                       "caught_stealing": 0, "double_play": 0,
                                       "wins": 0, "losses": 0, "shutouts": 0, "outs_recorded": 0,
                                       "hits_allowed": 0, "home_runs_allowed": 0, "strikeouts": 0,
                                       "walks_issued": 0, "batters_faced": 0, "runs_allowed": 0}

        game_statsheets[game["homePitcher"]] = {"plate_appearances": 0, "at_bats": 0, "struckouts": 0, "walks": 0,
                                                "hits": 0, "doubles": 0, "triples": 0, "quadruples": 0, "homeruns": 0,
                                                "runs": 0, "rbis": 0, "stolen_bases": 0,
                                                "caught_stealing": 0, "double_play": 0,
                                                "wins": 0, "losses": 0, "shutouts": 0, "outs_recorded": 0,
                                                "hits_allowed": 0, "home_runs_allowed": 0, "strikeouts": 0,
                                                "walks_issued": 0, "batters_faced": 0, "runs_allowed": 0}
        game_statsheets[game["awayPitcher"]] = {"plate_appearances": 0, "at_bats": 0, "struckouts": 0, "walks": 0,
                                                "hits": 0, "doubles": 0, "triples": 0, "quadruples": 0, "homeruns": 0,
                                                "runs": 0, "rbis": 0, "stolen_bases": 0,
                                                "caught_stealing": 0, "double_play": 0,
                                                "wins": 0, "losses": 0, "shutouts": 0, "outs_recorded": 0,
                                                "hits_allowed": 0, "home_runs_allowed": 0, "strikeouts": 0,
                                                "walks_issued": 0, "batters_faced": 0, "runs_allowed": 0}
        shakeup = False
        if len(game["outcomes"]) > 0:
            for outcome in game["outcomes"]:
                if "shuffled in the Reverb" in outcome:
                    shakeup = True
                    break
        if shakeup:
            continue

        for i in range(sim_length):
            game_log = [f'Day {game["day"]}.',
                        f'{game["homePitcherName"]} pitching for the {game["homeTeamName"]} at home.',
                        f'{game["awayPitcherName"]} pitching for the {game["awayTeamName"]} on the road.']
            home_score, away_score = 0, 0
            home_order, away_order = 0, 0
            home_strikeouts, away_strikeouts = 0, 0
            inning = 0
            while True:
                game_log.append(f'\nTop of the {inning+1}, {game["awayTeamNickname"]} batting.')
                game_log.append(f'{game["homeTeamNickname"]}: {home_score} -  {game["awayTeamNickname"]}: {away_score}')
                a_runs, away_order, a_strikeouts = await simulate_inning(model, away_lineup, away_order,
                                                                         game_statsheets, player_blood_types,
                                                                         game, True, game_log, player_names)

                away_score += a_runs
                away_strikeouts += a_strikeouts
                if inning == 8 and home_score != away_score:
                    break
                game_log.append(f'\nBottom of the {inning + 1}, {game["homeTeamNickname"]} batting.')
                game_log.append(f'{game["homeTeamNickname"]}: {home_score} -  {game["awayTeamNickname"]}: {away_score}')
                h_runs, home_order, h_strikeouts = await simulate_inning(model, home_lineup, home_order,
                                                                         game_statsheets, player_blood_types,
                                                                         game, False, game_log, player_names)
                home_score += h_runs
                home_strikeouts += h_strikeouts

                if inning >= 8 and home_score != away_score:
                    break
                inning += 1
            innings.append(inning+1)
            home_scores.append(home_score)
            away_scores.append(away_score)
            if home_score == 0:
                home_shutout += 1
                game_statsheets[game["awayPitcher"]]["shutouts"] += 1
            if away_score == 0:
                away_shutout += 1
                game_statsheets[game["homePitcher"]]["shutouts"] += 1
            if home_score > away_score:
                home_wins += 1
                game_statsheets[game["homePitcher"]]["wins"] += 1
                game_statsheets[game["awayPitcher"]]["losses"] += 1
                game_log.append(f'Game Over. {game["homeTeamName"]} win {home_score} - {away_score}')
            else:
                away_wins += 1
                game_statsheets[game["awayPitcher"]]["wins"] += 1
                game_statsheets[game["homePitcher"]]["losses"] += 1
                game_log.append(f'Game Over. {game["awayTeamName"]} win {away_score} - {home_score}')
            home_struckout.append(home_strikeouts)
            away_struckout.append(away_strikeouts)
            if i == 0:
                filename = os.path.join('pendant_data', 'test', 'season_sim', 'game_logs',
                                        f's{season}-d{day}_{away_name}-at-{home_name}.txt')
                with open(filename, 'w') as file:
                    for message in game_log:
                        file.write(f"{message}\n")

        home_scores.sort()
        away_scores.sort()
        home_struckout.sort(reverse=True)
        away_struckout.sort(reverse=True)

        home_odds, away_odds = game["homeOdds"], game["awayOdds"]

        if game['homeScore'] > game['awayScore']:
            if home_odds > away_odds:
                a_favored_wins += 1
        else:
            if away_odds > home_odds:
                a_favored_wins += 1
        if statistics.mean(home_scores) > statistics.mean(away_scores):
            if home_odds > away_odds:
                p_favored_wins += 1
        else:
            if away_odds > home_odds:
                p_favored_wins += 1

        avg_home_score = statistics.mean(home_scores)
        avg_away_score = statistics.mean(away_scores)
        if season == 10:
            avg_home_score = avg_home_score % 10
            avg_away_score = avg_away_score % 10
        if game['homeScore'] > game['awayScore']:
            if avg_home_score > avg_away_score:
                predicted_wins += 1
        else:
            if avg_away_score > avg_home_score:
                predicted_wins += 1

        strikeouts[game["homePitcher"]] = {
            "name": game["homePitcherName"],
            "predicted_strikeouts": statistics.mean(away_struckout),
            "sho_per": away_shutout / sim_length
        }
        strikeouts[game["awayPitcher"]] = {
            "name": game["awayPitcherName"],
            "predicted_strikeouts": statistics.mean(home_struckout),
            "sho_per": home_shutout / sim_length
        }

    with open(os.path.join('pendant_data', 'results', f"s{season}_d{day}_results.txt"), 'a') as fd:
        fd.write(output_text)
    return predicted_wins, a_favored_wins, strikeouts, game_statsheets


async def simulate_inning(model, lineup, order, stat_sheets, player_blood_types,
                          game, top_of_inning, game_log, player_names):
    season = game["season"]
    if top_of_inning:
        pitcher_id, hit_team_id, hit_team_name = game["homePitcher"], game["awayTeam"], game["awayTeamName"]
    else:
        pitcher_id, hit_team_id, hit_team_name = game["awayPitcher"], game["homeTeam"], game["homeTeamName"]
    bases = {1: 0, 2: 0, 3: 0}
    inning_outs = 0
    score = 0
    strikeouts = 0
    while True:
        hitter_id = list(lineup.keys())[order]
        if hitter_id not in model:
            order += 1
            if order == len(lineup):
                order = 0
            continue
        hitter = model[hitter_id]
        game_log.append(f'{player_names[hitter_id]} batting for the {hit_team_name}')
        outs, runs, bases, in_strikeouts = await simulate_at_bat(bases, hitter, stat_sheets, player_blood_types,
                                                                 pitcher_id, hitter_id, hit_team_id, season,
                                                                 game_log, player_names)
        inning_outs += outs
        strikeouts += in_strikeouts
        if inning_outs == 3:
            break
        score += runs
        order += 1
        if order == len(lineup):
            order = 0
    return score, order, strikeouts


async def simulate_at_bat(bases, hitter_model, stat_sheets, player_blood_types,
                          pitcher_id, hitter_id, hit_team_id, season, game_log, player_names):
    # [field_out %, strike_out %, walk %, single %, double %, triple %, hr %]
    play = await simulate_play(hitter_model)
    good_odds = random.random() < .66666
    outs, strikeouts, runs = 0, 0, 0
    stat_sheets[pitcher_id]["batters_faced"] += 1
    if "plate_appearances" not in stat_sheets[hitter_id]:
        print(hitter_id)
    stat_sheets[hitter_id]["plate_appearances"] += 1
    # field out?
    if play == 0:
        outs += 1
        if bases[3]:
            if not good_odds:
                runs += 1
                bases[3] = 0
        if bases[2] and not bases[3]:
            if good_odds:
                bases[3] = 1
                bases[2] = 0
        if bases[1] and not bases[2]:
            if good_odds:
                bases[2] = 1
                bases[1] = 0
        run_msg = ""
        if runs > 0:
            run_msg = f" {runs} scores."
        game_log.append(f'{player_names[hitter_id]} hit a ground/fly out.{run_msg}')
    # strikeout
    elif play == 1:
        outs += 1
        strikeouts += 1
        stat_sheets[hitter_id]["struckouts"] += 1
        stat_sheets[pitcher_id]["strikeouts"] += 1
        game_log.append(f'{player_names[hitter_id]} struck out.')
    # walk
    elif play == 2:
        base_instincts = False
        if hit_team_id in blood_effect:
            if "base_instincts" in blood_effect[hit_team_id]:
                if season >= blood_effect[hit_team_id]["base_instincts"]["season"]:
                    if hitter_id in player_blood_types:
                        if player_blood_types[hitter_id] == blood_effect[hit_team_id]["base_instincts"]["blood"]:
                            base_instincts = True
        complete = False
        base_msg = ""
        if base_instincts:
            complete = True
            walk_chance = random.random()
            if walk_chance < .035:
                advance = 3
                base_msg = " Base Instincts takes them to 3rd base."
                base_instincts_procs[season][3] += 1
            elif walk_chance < .19:
                advance = 2
                base_msg = " Base Instincts takes them to 2nd base."
                base_instincts_procs[season][2] += 1
            else:
                advance = 1
            if advance == 3:
                if bases[3]:
                    runs += 1
                    bases[3] = 0
                if bases[2]:
                    runs += 1
                    bases[2] = 0
                if bases[1]:
                    runs += 1
                    bases[1] = 0
                bases[3] = 1
            elif advance == 2:
                if bases[3]:
                    if bases[2] or bases[1]:
                        runs += 1
                        bases[3] = 0
                if bases[2]:
                    if bases[1]:
                        runs += 1
                    else:
                        bases[3] = 1
                    bases[2] = 0
                if bases[1]:
                    bases[1] = 0
                    bases[3] = 1
                bases[2] = 1
            else:
                complete = False

        if not complete:
            if bases[3]:
                if bases[2] and bases[1]:
                    runs += 1
                    bases[3] = 0
            if bases[2]:
                if bases[1]:
                    bases[2] = 0
                    bases[3] = 1
            if bases[1]:
                bases[1] = 0
                bases[2] = 1
            bases[1] = 1
        stat_sheets[hitter_id]["walks"] += 1
        stat_sheets[pitcher_id]["walks_issued"] += 1
        game_log.append(f'{player_names[hitter_id]} drew a walk.{base_msg}')
    # single
    elif play == 3:
        if bases[3]:
            runs += 1
            bases[3] = 0
        if bases[2]:
            if good_odds:
                runs += 1
            else:
                bases[3] = 1
            bases[2] = 0
        if bases[1]:
            if good_odds and bases[3]:
                bases[3] = 1
            else:
                bases[2] = 1
            bases[1] = 0
        bases[1] = 1
        stat_sheets[hitter_id]["hits"] += 1
        stat_sheets[pitcher_id]["hits_allowed"] += 1

        run_msg = ""
        if runs > 0:
            run_msg = f" {runs} scores."
        game_log.append(f'{player_names[hitter_id]} hit a single.{run_msg}')
    # double
    elif play == 4:
        if bases[3]:
            runs += 1
            bases[3] = 0
        if bases[2]:
            runs += 1
            bases[2] = 0
        if bases[1]:
            if not good_odds:
                bases[3] = 1
            else:
                runs += 1
            bases[1] = 0
        bases[2] = 1
        stat_sheets[hitter_id]["hits"] += 1
        stat_sheets[hitter_id]["doubles"] += 1
        stat_sheets[pitcher_id]["hits_allowed"] += 1
        run_msg = ""
        if runs > 0:
            run_msg = f" {runs} scores."
        game_log.append(f'{player_names[hitter_id]} hit a double.{run_msg}')
    # triple or hr
    elif play >= 5:
        if bases[3]:
            runs += 1
            bases[3] = 0
        if bases[2]:
            runs += 1
            bases[2] = 0
        if bases[1]:
            runs += 1
            bases[1] = 0
        # if triple
        if play == 5:
            bases[3] = 1
            stat_sheets[hitter_id]["triples"] += 1
            run_msg = ""
            if runs > 0:
                run_msg = f" {runs} scores."
            game_log.append(f'{player_names[hitter_id]} hit a triple.{run_msg}')
        else:
            runs += 1
            stat_sheets[hitter_id]["homeruns"] += 1
            stat_sheets[pitcher_id]["home_runs_allowed"] += 1
            run_msg = ""
            if runs > 0:
                run_msg = f" {runs} scores."
            game_log.append(f'{player_names[hitter_id]} hit a home run.{run_msg}')

        stat_sheets[hitter_id]["hits"] += 1
        stat_sheets[pitcher_id]["hits_allowed"] += 1

    if play != 2:
        stat_sheets[hitter_id]["at_bats"] += 1
    stat_sheets[hitter_id]["rbis"] += runs
    stat_sheets[pitcher_id]["outs_recorded"] += outs
    stat_sheets[pitcher_id]["runs_allowed"] += runs
    return outs, runs, bases, strikeouts


async def simulate_play(hitter, roll=None):
    if not roll:
        # generate random float between 0-1
        roll = random.random()
    total = 0
    # hitter is an array of probabilities for 7 outcomes
    # ['field_out %', 'strike_out %', 'walk %', 'single %', 'double %', 'triple %', 'hr %']
    for i in range(len(hitter)):
        # add the odds of the next outcome to the running total
        total += hitter[i]
        # if the random roll is less than the new total, return this outcome
        if roll < total:
            return i


async def test_at_bat():
    probs = [0.52720077, 0.10775841, 0.04588508, 0.13242703, 0.03449444, 0.06527878, 0.08695549]
    roll = .4
    print(await simulate_at_bat(probs, roll) == 0)
    roll = .53
    print(await simulate_at_bat(probs, roll) == 1)
    roll = .64
    print(await simulate_at_bat(probs, roll) == 2)
    roll = .681
    print(await simulate_at_bat(probs, roll) == 3)
    roll = .814
    print(await simulate_at_bat(probs, roll) == 4)
    roll = .848
    print(await simulate_at_bat(probs, roll) == 5)
    roll = .914
    print(await simulate_at_bat(probs, roll) == 6)


async def test_walks():
    bases, runs = test_walks_i(True, {1: 1, 2: 1, 3: 0}, 0, .02)
    print(bases[1]==0 and bases[2]==0 and bases[3]==1 and runs == 2)
    bases, runs = test_walks_i(True, {1: 0, 2: 1, 3: 1}, 0, .02)
    print(bases[1]==0 and bases[2]==0 and bases[3]==1 and runs == 2)

    bases, runs = test_walks_i(False, {1: 1, 2: 1, 3: 0}, 0, .02)
    print(bases[1]==1 and bases[2]==1 and bases[3]==1 and runs == 0)
    bases, runs = test_walks_i(False, {1: 0, 2: 1, 3: 1}, 0, .02)
    print(bases[1]==1 and bases[2]==1 and bases[3]==1 and runs == 0)

    bases, runs = test_walks_i(True, {1: 1, 2: 0, 3: 1}, 0, .02)
    print(bases[1]==0 and bases[2]==0 and bases[3]==1 and runs == 2)
    bases, runs = test_walks_i(True, {1: 1, 2: 0, 3: 1}, 0, .05)
    print(bases[1]==0 and bases[2]==1 and bases[3]==1 and runs == 1)


def test_walks_i(base_instincts, bases, runs, walk_chance=None):
    complete = False
    if base_instincts:
        complete = True
        if not walk_chance:
            walk_chance = random.random()
        if walk_chance < .035:
            advance = 3
        elif walk_chance < .19:
            advance = 2
        else:
            advance = 1
        if advance == 3:
            if bases[3]:
                runs += 1
                bases[3] = 0
            if bases[2]:
                runs += 1
                bases[2] = 0
            if bases[1]:
                runs += 1
                bases[1] = 0
            bases[3] = 1
        elif advance == 2:
            if bases[3]:
                if bases[2] or bases[1]:
                    runs += 1
                    bases[3] = 0
            if bases[2]:
                if bases[1]:
                    runs += 1
                else:
                    bases[3] = 1
                bases[2] = 0
            if bases[1]:
                bases[1] = 0
                bases[3] = 1
            bases[2] = 1
        else:
            complete = False

    if not complete:
        if bases[3]:
            if bases[2] and bases[1]:
                runs += 1
                bases[3] = 0
        if bases[2]:
            if bases[1]:
                bases[2] = 0
                bases[3] = 1
        if bases[1]:
            bases[1] = 0
            bases[2] = 1
        bases[1] = 1
    return bases, runs


async def setup(sim_length):
    clf = load(os.path.join("pendant_data", "ab_model", "ab.joblib"))

    for season in range(7, 11):
        print(f"season {season}")
        outcomes = []
        comp_sum = 0
        outcome_text = ""
        daily_strikeouts = {}
        with open(os.path.join('pendant_data', 'test', 'season_sim', 'season_data', f"season{season+1}.json"), 'r',
                  encoding='utf8') as json_file:
            raw_season_data = json.load(json_file)
        s_predicted_wins, s_a_favored_wins = 0, 0
        season_data = {}
        season_statsheets = {}
        for game in raw_season_data:
            if game['day'] not in season_data:
                season_data[game['day']] = []
            season_data[game['day']].append(game)
        for day in range(0, 99):
            games = season_data[day]
            if day % 25 == 0:
                print(f"day {day}")
            with open(os.path.join('pendant_data', 'test', 'season_sim', 'stlats', f"s{season}_d{day}_stlats.json"), 'r', encoding='utf8') as json_file:
                player_stlats_list = json.load(json_file)
            player_stlats = {}
            team_stlats = {}
            player_blood_types = {}
            player_names = {}
            for player in player_stlats_list:
                player_stlats[player["player_id"]] = player
                player_blood_types[player["player_id"]] = player["blood"]
                player_names[player["player_id"]] = player["player_name"]
                if player["team_id"] not in team_stlats:
                    team_stlats[player["team_id"]] = {"lineup": {}}
                if player["position_type_id"] == '0':
                    player_id = player["player_id"]
                    team_stlats[player["team_id"]]["lineup"][player_id] = player
            for team in team_stlats:
                us_lineup = team_stlats[team]["lineup"]
                sorted_lineup = {k: v for k, v in
                                 sorted(us_lineup.items(), key=lambda item: item[1]["position_id"])}
                team_stlats[team]["lineup"] = sorted_lineup

            model = await setup_models(games, clf, player_stlats, team_stlats)

            predicted_wins, a_favored_wins, strikeouts, stat_sheets = await simulate(games, model,
                                                                                     team_stlats,
                                                                                     player_blood_types,
                                                                                     player_names, sim_length)

            daily_strikeouts[day] = strikeouts
            s_predicted_wins += predicted_wins
            s_a_favored_wins += a_favored_wins

            for player in stat_sheets:
                if player not in season_statsheets:
                    season_statsheets[player] = {"plate_appearances": 0, "at_bats": 0, "struckouts": 0, "walks": 0,
                                          "hits": 0, "doubles": 0, "triples": 0, "quadruples": 0, "homeruns": 0,
                                          "runs": 0, "rbis": 0, "stolen_bases": 0,
                                          "caught_stealing": 0, "double_play": 0,
                                          "wins": 0, "losses": 0, "shutouts": 0, "outs_recorded": 0,
                                          "hits_allowed": 0, "home_runs_allowed": 0, "strikeouts": 0,
                                          "walks_issued": 0, "batters_faced": 0, "runs_allowed": 0}
                adjust_gs = {k: v / sim_length for k, v in stat_sheets[player].items()}
                for key in adjust_gs:
                    season_statsheets[player][key] += adjust_gs[key]
        for player in season_statsheets:
            season_statsheets[player] = {k: round(v) for k, v in season_statsheets[player].items()}
        with open(os.path.join('pendant_data', 'results', f"{season}_outcomes_{sim_length}.txt"), 'w', encoding='utf8') as fd:
            fd.write(outcome_text)
        s_predicted_wins_per = round((s_predicted_wins / 990) * 1000) / 10
        s_a_favored_wins_per = round((s_a_favored_wins / 990) * 1000) / 10
        print(f"{s_predicted_wins} ({s_predicted_wins_per}%) favored wins predicted - "
              f"{s_a_favored_wins} ({s_a_favored_wins_per}%) actual favored wins. ")

        with open(os.path.join('pendant_data', 'results', f"{season}_k_sho_results_{sim_length}.json"), 'w',
                  encoding='utf8') as json_file:
            json.dump(daily_strikeouts, json_file)
        with open(os.path.join('pendant_data', 'results', f"{season}_statsheets_{sim_length}.json"), 'w',
                  encoding='utf8') as json_file:
            json.dump(season_statsheets, json_file)
    print(base_instincts_procs)


async def add_order(day, season):
    with open(os.path.join('pendant_data', 'test', f"{season}_{day}player_statsheets.json"), 'r', encoding='utf8') as json_file:
        player_statsheets = json.load(json_file)
    with open(os.path.join('pendant_data', 'test', f"s{season}_d{day}_team_stlats.json"), 'r', encoding='utf8') as json_file:
        team_stlats = json.load(json_file)
    with open(os.path.join('pendant_data', 'test', f"s{season}_d{day}_pitcher_stlats.json"), 'r', encoding='utf8') as json_file:
        pitcher_stlats = json.load(json_file)
    team_orders = {
        "b72f3061-f573-40d7-832a-5ad475bd7909": 0,
        "878c1bf6-0d21-4659-bfee-916c8314d69c": 0,
        "b024e975-1c4a-4575-8936-a3754a08806a": 0,
        "adc5b394-8f76-416d-9ce9-813706877b84": 0,
        "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16": 0,
        "bfd38797-8404-4b38-8b82-341da28b1f83": 0,
        "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e": 0,
        "979aee4a-6d80-4863-bf1c-ee1a78e06024": 0,
        "7966eb04-efcc-499b-8f03-d13916330531": 0,
        "36569151-a2fb-43c1-9df7-2df512424c82": 0,
        "8d87c468-699a-47a8-b40d-cfb73a5660ad": 0,
        "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5": 0,
        "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7": 0,
        "f02aeae2-5e6a-4098-9842-02d2273f25c7": 0,
        "57ec08cc-0411-4643-b304-0e80dbc15ac7": 0,
        "747b8e4a-7e50-4638-a973-ea7950a3e739": 0,
        "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff": 0,
        "b63be8c2-576a-4d6e-8daf-814f8bcea96f": 0,
        "105bc3ff-1320-4e37-8ef0-8d595cb95dd0": 0,
        "a37f9158-7f82-46bc-908c-c9e2dda7c33b": 0,
        'c73b705c-40ad-4633-a6ed-d357ee2e2bcf': 0
    }
    for statsheet in player_statsheets[0].values():
        if statsheet["position"] == "lineup":
            if statsheet["playerId"] in team_stlats[statsheet["teamId"]]["lineup"]:
                order = team_orders[statsheet["teamId"]]
                team_stlats[statsheet["teamId"]]["lineup"][statsheet["playerId"]]["order"] = order
                team_stlats[statsheet["teamId"]]["lineup"][statsheet["playerId"]]["team"] = statsheet["teamId"]
                team_orders[statsheet["teamId"]] += 1

        else:
            pitcher_stlats[statsheet["playerId"]]["team"] = statsheet["teamId"]
    with open(os.path.join('pendant_data', 'test', f"s{season}_d{day}_team_stlats_order.json"), 'w', encoding='utf8') as json_file:
        json.dump(team_stlats, json_file)


async def sum_strikeouts(length):
    print(f"strikeout avgs at sim length {length}")
    for season in range(7, 11):
        print(season)
        strikeouts = {}
        with open(os.path.join('pendant_data', 'results', f"{season}_k_sho_results_{length}.json"), 'r',
                  encoding='utf8') as json_file:
            daily_strikeouts = json.load(json_file)
        for day in daily_strikeouts:
            for pid in daily_strikeouts[day]:
                if pid not in strikeouts:
                    strikeouts[pid] = {"name": daily_strikeouts[day][pid]["name"], "strikeouts": 0}
                strikeouts[pid]["strikeouts"] += daily_strikeouts[day][pid]["predicted_strikeouts"]
        sorted_strikeouts = {k: v for k, v in
                            sorted(strikeouts.items(), key=lambda item: item[1]["strikeouts"], reverse=True)}
        print(sorted_strikeouts.values())

async def get_real_stats():
    for season in range(7, 11):
        with open(os.path.join('pendant_data', 'results', f"{season}_statsheets_1000.json"), 'r',
                  encoding='utf8') as json_file:
            season_statsheets = json.load(json_file)
        pitcher_ids = []
        hitter_ids = []
        for pid, values in season_statsheets.items():
            if values["plate_appearances"] > 0:
                hitter_ids.append(pid)
            if values["outs_recorded"] > 0:
                pitcher_ids.append(pid)
        pitcher_stats = {}
        hitter_stats = {}
        chunked_player_ids = [pitcher_ids[i:i + 50] for i in range(0, len(pitcher_ids), 50)]
        for chunk in chunked_player_ids:
            pids = ','.join(chunk)
            url = f"https://api.blaseball-reference.com/v1/playerStats?category=pitching&season={season}&playerIds={pids}"
            response = await retry_request(url)
            player_stats = response.json()
            for player in player_stats:
                pitcher_stats[player["player_id"]] = player
        chunked_player_ids = [hitter_ids[i:i + 50] for i in range(0, len(hitter_ids), 50)]
        for chunk in chunked_player_ids:
            pids = ','.join(chunk)
            url = f"https://api.blaseball-reference.com/v1/playerStats?category=batting&season={season}&playerIds={pids}"
            response = await retry_request(url)
            player_stats = response.json()
            for player in player_stats:
                hitter_stats[player["player_id"]] = player
        season_stats = {"hitting": hitter_stats, "pitching": pitcher_stats}
        with open(os.path.join('pendant_data', 'results', 'actual_stats', f"{season}_actual_stats.json"), 'w',
                  encoding='utf8') as json_file:
            json.dump(season_stats, json_file)

async def compare_stats(length):
    for season in range(7, 11):
        with open(os.path.join('pendant_data', 'results', f"{season}_statsheets_{length}.json"), 'r',
                  encoding='utf8') as json_file:
            predicted_statsheets = json.load(json_file)
        with open(os.path.join('pendant_data', 'results', 'actual_stats', f"{season}_actual_stats.json"), 'r',
                  encoding='utf8') as json_file:
            actual_statsheets = json.load(json_file)
        hitting_diffs = {"below": {}, "above": {}}
        pitching_diffs = {"below": {}, "above": {}}
        for pid, values in predicted_statsheets.items():
            if values["plate_appearances"] > 0 and pid in actual_statsheets["hitting"]:
                hitting_diffs["below"][pid] = {}
                hitting_diffs["above"][pid] = {}
                for key in ["plate_appearances", "at_bats", "struckouts", "walks",
                            "hits", "doubles", "triples", "homeruns", "rbis"]:
                    okey = key
                    if key == "struckouts":
                        okey = "strikeouts"
                    if key == "rbis":
                        okey = "runs_batted_in"
                    if key == "homeruns":
                        okey = "home_runs"
                    actual = float(actual_statsheets["hitting"][pid][okey])
                    predicted = values[key]
                    if actual > predicted:
                        percent_diff = 1 - (predicted / actual)
                        hitting_diffs["below"][pid][key] = percent_diff
                    else:
                        percent_diff = 1 - (actual / predicted)
                        hitting_diffs["above"][pid][key] = percent_diff
            if values["outs_recorded"] > 0 and pid in actual_statsheets["pitching"]:
                pitching_diffs["below"][pid] = {}
                pitching_diffs["above"][pid] = {}
                for key in ["outs_recorded", "hits_allowed",
                            "home_runs_allowed", "strikeouts", "walks_issued"]:
                    okey = key
                    if key == "home_runs_allowed":
                        okey = "hrs_allowed"
                    if key == "walks_issued":
                        okey = "walks"
                    actual = float(actual_statsheets["pitching"][pid][okey])
                    predicted = values[key]
                    if actual > predicted:
                        percent_diff = 1 - (predicted / actual)
                        pitching_diffs["below"][pid][key] = percent_diff
                    else:
                        percent_diff = 1 - (actual / predicted)
                        pitching_diffs["above"][pid][key] = percent_diff

        with open(os.path.join('pendant_data', 'results', 'stats', f"{season}_hitting_stat_diffs.json"), 'w',
                  encoding='utf8') as json_file:
            json.dump(hitting_diffs, json_file)
        with open(os.path.join('pendant_data', 'results', 'stats', f"{season}_pitching_stat_diffs.json"), 'w',
                  encoding='utf8') as json_file:
            json.dump(pitching_diffs, json_file)


async def summarize_diffs():
    all_diffs = {"hitting": {"above": {"plate_appearances": [], "at_bats": [], "struckouts": [],
                                       "walks": [], "hits": [], "doubles": [], "triples": [],
                                       "homeruns": [], "rbis": []},
                             "below": {"plate_appearances": [], "at_bats": [], "struckouts": [],
                                       "walks": [], "hits": [], "doubles": [], "triples": [],
                                       "homeruns": [], "rbis": []}},
                 "pitching": {"above": {"outs_recorded": [], "hits_allowed": [], "home_runs_allowed": [],
                                        "strikeouts": [], "walks_issued": []},
                              "below": {"outs_recorded": [], "hits_allowed": [], "home_runs_allowed": [],
                                        "strikeouts": [], "walks_issued": []}}}

    def summary_message(stat_dict):
        summary_msg = ""
        for stat, stat_list in stat_dict.items():
            stat_list.sort()
            p_stat_list = score_percentiles(stat_list)
            p_stat_list = [str(round(float(p) * 100000) / 100000) for p in p_stat_list]
            min_d, max_d = round(stat_list[0] * 100000) / 100000, round(stat_list[-1] * 100000) / 100000
            summary_msg += f"{stat} min diff: {min_d}, max diff: {max_d}, avg: {round(statistics.mean(stat_list) * 100000) / 100000}, " \
                           f"(50, 75, 90, 99)th percentiles: {', '.join(p_stat_list)}\n"
        return summary_msg

    for season in range(7, 11):
        with open(os.path.join('pendant_data', 'results', 'stats', f"{season}_hitting_stat_diffs.json"), 'r',
                  encoding='utf8') as json_file:
            hitting_diffs = json.load(json_file)
        with open(os.path.join('pendant_data', 'results', 'stats', f"{season}_pitching_stat_diffs.json"), 'r',
                  encoding='utf8') as json_file:
            pitching_diffs = json.load(json_file)
        season_diffs = {"hitting": {"above": {"plate_appearances": [], "at_bats": [], "struckouts": [],
                                              "walks": [], "hits": [], "doubles": [], "triples": [],
                                              "homeruns": [], "rbis": []},
                                    "below": {"plate_appearances": [], "at_bats": [], "struckouts": [],
                                              "walks": [], "hits": [], "doubles": [], "triples": [],
                                              "homeruns": [], "rbis": []}},
                        "pitching": {"above": {"outs_recorded": [], "hits_allowed": [], "home_runs_allowed": [],
                                               "strikeouts": [], "walks_issued": []},
                                     "below": {"outs_recorded": [], "hits_allowed": [], "home_runs_allowed": [],
                                               "strikeouts": [], "walks_issued": []}}}
        for diff in hitting_diffs["above"].values():
            for key in diff:
                season_diffs["hitting"]["above"][key].append(diff[key])
                all_diffs["hitting"]["above"][key].append(diff[key])
        for diff in hitting_diffs["below"].values():
            for key in diff:
                season_diffs["hitting"]["below"][key].append(diff[key])
                all_diffs["hitting"]["below"][key].append(diff[key])
        for diff in pitching_diffs["above"].values():
            for key in diff:
                season_diffs["pitching"]["above"][key].append(diff[key])
                all_diffs["pitching"]["above"][key].append(diff[key])
        for diff in pitching_diffs["below"].values():
            for key in diff:
                season_diffs["pitching"]["below"][key].append(diff[key])
                all_diffs["pitching"]["below"][key].append(diff[key])
        p_idxs = [.50, .75, .90, .99]

        def score_percentiles(scores):
            count = len(scores)
            prob_vals = []
            for p in p_idxs:
                idx = round((p * count) - 1)
                prob_vals.append(scores[idx])
            return [str(v) for v in prob_vals]

        hitting_msg_a = summary_message(season_diffs["hitting"]["above"])
        hitting_msg_b = summary_message(season_diffs["hitting"]["below"])
        pitching_msg_a = summary_message(season_diffs["pitching"]["above"])
        pitching_msg_b = summary_message(season_diffs["pitching"]["below"])
        print(f"Season {season} stat diffs above actual\n{hitting_msg_a}\n{pitching_msg_a}")
        print(f"Season {season} stat diffs below actual\n{hitting_msg_b}\n{pitching_msg_b}")

    hitting_msg_a = summary_message(all_diffs["hitting"]["above"])
    hitting_msg_b = summary_message(all_diffs["hitting"]["below"])
    pitching_msg_a = summary_message(all_diffs["pitching"]["above"])
    pitching_msg_b = summary_message(all_diffs["pitching"]["below"])
    print(f"Seasons 8-11 cumulative stat diffs above actual\n{hitting_msg_a}\n{pitching_msg_a}")
    print(f"Seasons 8-11 cumulative stat diffs below actual\n{hitting_msg_b}\n{pitching_msg_b}")


loop = asyncio.get_event_loop()

loop.run_until_complete(setup(1000))
loop.run_until_complete(sum_strikeouts(1000))
loop.run_until_complete(compare_stats(1000))
loop.run_until_complete(summarize_diffs())
loop.close()
