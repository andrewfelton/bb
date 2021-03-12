
class lsettings:

    def __init__(self, league_type):
        import sys
        sys.path.append('python/utilities')
        import utilities

        if (league_type=='SoS'):
            self.num_teams = 16
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp','ops']

            self.pitching_counting_stats = ['qs','so','sv', 'hld']
            self.pitching_rate_stats = ['era', 'whip']

            self.batting_split = .55
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5

        elif (league_type=='Legacy'):
            self.num_teams = 12
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp']

            self.pitching_counting_stats = ['ip','so','svhld']
            self.pitching_rate_stats = ['era', 'whip']

            self.batting_split = .55
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5

        self.hitting_stats = utilities.flatten([self.hitting_rate_stats, self.hitting_counting_stats])
        self.pitching_stats = utilities.flatten([self.pitching_rate_stats, self.pitching_counting_stats])


