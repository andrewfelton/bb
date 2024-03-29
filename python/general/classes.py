class league:
    def normalize_z_weights(self, zwgts):
        z_sum = sum(list(zwgts.values()))
        for key in list(zwgts.keys()):
            zwgts[key] = zwgts[key] * len(zwgts) / z_sum
        return zwgts

    def __init__(self, league_type):
        import sys
        sys.path.append('python/general')
        from general import utilities

        self.league_name = league_type
        self.name = self.league_name
        self.year = 2021

        if (league_type=='SoS'):
            self.league_platform = 'fleaflicker'
            self.league_num = '23172'

            self.num_teams = 16
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp','ops']
            self.hitting_other_stats = ['ab']
            self.z_weights_nominal_hitting = {
                #'hr':1, 'r':1, 'rbi':1, 'sb':1.1, 'obp':1.3, 'ops':1.2
                'hr': 1, 'r': 1, 'rbi': 1, 'sb': 1, 'obp': 1.1, 'ops': 1.1
            }
            self.z_weights_hitting = self.normalize_z_weights(self.z_weights_nominal_hitting)

            self.pitching_counting_stats = ['qs','so','sv', 'hld']
            self.pitching_rate_stats = ['era', 'whip']
            self.pitching_other_stats = ['gs', 'g']
            self.z_weights_nominal_pitching = {
                #'qs':1.2, 'so':1, 'sv':.9, 'hld':.6, 'era':1.2, 'whip':1.2
                'qs':1, 'so':1.1, 'sv':1, 'hld':1, 'era':1, 'whip':1
            }
            self.z_weights_pitching = self.normalize_z_weights(self.z_weights_nominal_pitching)

            self.z_weights = {**self.z_weights_hitting, **self.z_weights_pitching}
            self.batting_split = .6
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5


        elif (league_type=='Legacy'):
            self.league_platform = 'yahoo'
            self.league_num = '26574'

            self.num_teams = 12
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp']
            self.z_weights_nominal_hitting = {
                'hr':1, 'r':1, 'rbi':1, 'sb':.2, 'obp':1
            }
            self.z_weights_hitting = self.normalize_z_weights(self.z_weights_nominal_hitting)

            self.pitching_counting_stats = ['ip','so','svhld']
            self.pitching_rate_stats = ['era', 'whip']
            self.z_weights_nominal_pitching = {
                'ip':1, 'so':1, 'svhld':.8, 'era':1, 'whip':1
            }
            self.z_weights_pitching = self.normalize_z_weights(self.z_weights_nominal_pitching)

            self.z_weights = {**self.z_weights_hitting, **self.z_weights_pitching}
            self.batting_split = .6
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5

        self.hitting_stats = utilities.flatten([self.hitting_rate_stats, self.hitting_counting_stats])
        self.pitching_stats = utilities.flatten([self.pitching_rate_stats, self.pitching_counting_stats])


class FantasyTeam:
    def __init__(self, name):
        self.name = name
        self.players = []

    def add_player(self, player_name, player_ff_id=None):
        self.players.append(Player(player_name, player_ff_id))

    def to_dataframe(self):
        import pandas as pd
        roster = []
        for player in self.players:
            roster.append([self.name, player.name, player.ff_id])
        roster = pd.DataFrame(roster, columns=['Team', 'Player', 'ff_id'])
        return roster

    def __repr__(self):
        mystr = self.name
        if (len(self.players)>0):
            for player in self.players:
                mystr = mystr + '\n' + player.name
        return mystr


class Player:
    def __init__(self, name, ff_id=None):
        self.name = name
        self.ff_id = ff_id
        self.elig = None
        self.projections = None

    def __repr__(self):
        return self.name + '(' + self.ff_id + ')'


class PlayerFF(Player):
    def __init__(self, ff_name, ff_id, ff_url):
        self.ff_name = ff_name
        self.ff_id = ff_id
        self.ff_url = ff_url

    def __repr__(self):
        return self.name + '(' + self.ff_id + ')'


class FantasyTeamFF(FantasyTeam):
    1==1

