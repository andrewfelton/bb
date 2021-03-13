
class lsettings:
    def normalize_z_weights(self, zwgts):
        z_sum = sum(list(zwgts.values()))
        for key in list(zwgts.keys()):
            zwgts[key] = zwgts[key] * len(zwgts) / z_sum
        return zwgts

    def __init__(self, league_type):
        import sys
        sys.path.append('python/utilities')
        import utilities

        if (league_type=='SoS'):
            self.num_teams = 16
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp','ops']
            self.z_weights_nominal_hitting = {
                'hr':1, 'r':1, 'rbi':1, 'sb':1.3, 'obp':1, 'ops':1
            }
            self.z_weights_hitting = self.normalize_z_weights(self.z_weights_nominal_hitting)

            self.pitching_counting_stats = ['qs','so','sv', 'hld']
            self.pitching_rate_stats = ['era', 'whip']
            self.z_weights_nominal_pitching = {
                'qs':1, 'so':1, 'sv':.9, 'hld':.6, 'era':1, 'whip':1
            }
            self.z_weights_pitching = self.normalize_z_weights(self.z_weights_nominal_pitching)

            self.z_weights = {**self.z_weights_hitting, **self.z_weights_pitching}
            self.batting_split = .55
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5


        elif (league_type=='Legacy'):
            self.num_teams = 12
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp']
            self.z_weights_nominal_hitting = {
                'hr':1, 'r':1, 'rbi':1, 'sb':1.3, 'obp':1
            }
            self.z_weights_hitting = self.normalize_z_weights(self.z_weights_nominal_hitting)

            self.pitching_counting_stats = ['ip','so','svhld']
            self.pitching_rate_stats = ['era', 'whip']
            self.z_weights_nominal_pitching = {
                'ip':1, 'so':1, 'svhld':.8, 'era':1, 'whip':1
            }
            self.z_weights_pitching = self.normalize_z_weights(self.z_weights_nominal_pitching)

            self.z_weights = {**self.z_weights_hitting, **self.z_weights_pitching}
            self.batting_split = .55
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5

        self.hitting_stats = utilities.flatten([self.hitting_rate_stats, self.hitting_counting_stats])
        self.pitching_stats = utilities.flatten([self.pitching_rate_stats, self.pitching_counting_stats])


