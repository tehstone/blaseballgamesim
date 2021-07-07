
import csv

from eval import Eval
from team_state import TeamState
from stadium import Stadium
from common import BlaseballStatistics as Stats
from common import ForbiddenKnowledge as FK
from common import AdditiveTypes, BloodType, PlayerBuff, Team, Weather


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

batter_file = "../season_sim/eval/batters.csv"
pitcher_file = "../season_sim/eval/pitchers-sibr.csv"

lineup = {}
rotation = {}
stlats = {}
buffs = {}
names = {}
game_stats = {}

with open(batter_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 1
    for row in csv_reader:
        name = row[0]
        buo = row[1]
        div = row[2]
        mar = row[3]
        mox = row[4]
        mus = row[5]
        thw = row[6]
        trg = row[7]
        bth = row[8]
        con = row[9]
        grf = row[10]
        ind = row[11]
        lsr = row[12]
        prs = row[13]
        cin = row[14]
        pth = row[15]
        lineup[line_count] = name
        names[name] = name
        buffs[name] = {}
        game_stats[name] = {}
        stlats[name] = {
            FK.BUOYANCY: float(buo),
            FK.DIVINITY: float(div),
            FK.MARTYRDOM: float(mar),
            FK.MOXIE: float(mox),
            FK.MUSCLITUDE: float(mus),
            FK.THWACKABILITY: float(thw),
            FK.TRAGICNESS: float(trg),
            FK.BASE_THIRST: float(bth),
            FK.CONTINUATION: float(con),
            FK.GROUND_FRICTION: float(grf),
            FK.INDULGENCE: float(ind),
            FK.LASERLIKENESS: float(lsr),
            FK.PRESSURIZATION: float(prs),
            FK.CINNAMON: float(cin),
            FK.PATHETICISM: float(pth),
            FK.ANTICAPITALISM: 0.773526430988913,
            FK.CHASINESS: 0.826184892943561,
            FK.OMNISCIENCE: 0.7901157143783870,
            FK.TENACIOUSNESS: 0.8133712472630720,
            FK.WATCHFULNESS: 0.7665729800544850,
            FK.VIBES: 0.5,
        }
        line_count = line_count + 1

with open(pitcher_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 1
    for row in csv_reader:
        #print(f'row={row}')
        name = row[0]
        col = row[1]
        ovp = row[2]
        rth = row[3]
        ssp = row[4]
        sup = row[5]
        uth = row[6]
        prs = row[7]
        cin = row[8]
        buo = row[9]
        rotation[line_count] = name
        names[name] = name
        buffs[name] = {}
        stlats[name] = {
            FK.BUOYANCY: float(buo),
            FK.COLDNESS: float(col),
            FK.OVERPOWERMENT: float(ovp),
            FK.RUTHLESSNESS: float(rth),
            FK.SHAKESPEARIANISM: float(ssp),
            FK.SUPPRESSION: float(sup),
            FK.UNTHWACKABILITY: float(uth),
            FK.PRESSURIZATION: float(prs),
            FK.CINNAMON: float(cin),
            FK.ANTICAPITALISM: 0.773526430988913,
            FK.CHASINESS: 0.826184892943561,
            FK.OMNISCIENCE: 0.7901157143783870,
            FK.TENACIOUSNESS: 0.8133712472630720,
            FK.WATCHFULNESS: 0.7665729800544850,
            FK.VIBES: 0.5,
        }
        line_count = line_count + 1

home_team = TeamState(
            team_id="pitcher-eval",
            season=1,
            day=1,
            stadium=default_stadium,
            weather=Weather.ECLIPSE,
            is_home=True,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup=lineup,
            rotation=rotation,
            starting_pitcher=rotation[1],
            cur_pitcher_pos=1,
            stlats=stlats,
            buffs=buffs,
            game_stats={},
            segmented_stats={},
            blood={},
            player_names=names,
            cur_batter_pos=1,
        )

away_team = TeamState(
            team_id="batter-eval",
            season=1,
            day=1,
            stadium=default_stadium,
            weather=Weather.ECLIPSE,
            is_home=False,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup=lineup,
            rotation=rotation,
            starting_pitcher=rotation[1],
            cur_pitcher_pos=1,
            stlats=stlats,
            buffs=buffs,
            game_stats={},
            segmented_stats={},
            blood={},
            player_names=names,
            cur_batter_pos=1,
        )

eval = Eval(
    home_team,
    away_team,
    3,
    4,
)

eval.simulate_game()

print('name,walks_per_batter,outs_per_batter,strikeouts_per_batter,hits_per_batter,doubles_per_batter,triples_per_batter,hr_per_batter')
for key in home_team.game_stats:
    batters_faced = home_team.game_stats[key][Stats.PITCHER_BATTERS_FACED]
    walks_per_batter = home_team.game_stats[key][Stats.PITCHER_WALKS] / batters_faced
    outs = home_team.game_stats[key][Stats.PITCHER_STRIKEOUTS] + home_team.game_stats[key][Stats.PITCHER_FLYOUTS] + \
           home_team.game_stats[key][Stats.PITCHER_GROUNDOUTS]
    outs_per_batter = outs / batters_faced
    k_per_batter = home_team.game_stats[key][Stats.PITCHER_STRIKEOUTS] / batters_faced
    hits_per_batter = home_team.game_stats[key][Stats.PITCHER_HITS_ALLOWED] / batters_faced
    doubles_per_batter = home_team.game_stats[key][Stats.PITCHER_DOUBLE_ALLOWED] / batters_faced
    triples_per_batter = home_team.game_stats[key][Stats.PITCHER_TRIPLE_ALLOWED] / batters_faced
    hr_per_batter = home_team.game_stats[key][Stats.PITCHER_HRS_ALLOWED] / batters_faced
    print(f'{key},{walks_per_batter},{outs_per_batter},{k_per_batter},{hits_per_batter},{doubles_per_batter},{triples_per_batter},{hr_per_batter}')
    ##print(f'Summary for {key}')
    ##print(f'\twalks per batter = {home_team.game_stats[key][Stats.PITCHER_WALKS] / batters_faced}')
    ##print(f'\touts per batter = {outs / batters_faced}')
    ##print(f'\t\tstrikeouts per batter = {home_team.game_stats[key][Stats.PITCHER_STRIKEOUTS] / batters_faced}')
    ##print(f'\thits per batter = {home_team.game_stats[key][Stats.PITCHER_HITS_ALLOWED] / batters_faced}')
    ##print(f'\t\tdouble per batter = {home_team.game_stats[key][Stats.PITCHER_DOUBLE_ALLOWED] / batters_faced}')
    ##print(f'\t\ttriple per batter = {home_team.game_stats[key][Stats.PITCHER_TRIPLE_ALLOWED] / batters_faced}')
    ##print(f'\t\thome runs per batter = {home_team.game_stats[key][Stats.PITCHER_HRS_ALLOWED] / batters_faced}')
    ##print('')


