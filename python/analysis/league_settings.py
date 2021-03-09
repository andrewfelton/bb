
class league_settings:

    def __init__(self, league_type):
        import itertools

        if (league_type=='SoS'):
            self.num_teams = 16
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp','ops']

            self.pitching_counting_stats = ['qs','so','sv', 'hld']
            self.pitching_rate_stats = ['era', 'whip']

            self.batting_split = .65
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5

        elif (league_type=='Legacy'):
            self.num_teams = 12
            self.hitting_counting_stats = ['hr','r','rbi','sb']
            self.hitting_rate_stats = ['obp']

            self.pitching_counting_stats = ['ip','so','svhld']
            self.pitching_rate_stats = ['era', 'whip']

            self.batting_split = .65
            self.hitters_per_team = 12.5
            self.pitchers_per_team = 12.5

        self.hitting_stats = list(itertools.chain(*[hitting_rate_stats, hitting_counting_stats]))
        self.pitching_stats = list(itertools.chain(*[pitching_rate_stats, pitching_counting_stats]))


