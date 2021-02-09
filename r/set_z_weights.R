


# set the Z weights
rate_stats_pitching = c('ERA', 'WHIP')
counting_stats_pitching =   c('QS', 'SV', 'HLD', 'SO')
raw_weights_pitching <- create_weights_df(
  c(rate_stats_pitching, counting_stats_pitching),
  c(1.1, 1.1, 1.2, .9, .6, 1)
)

rate_stats_hitting = c('OBP', 'OPS')
counting_stats_hitting = c('HR', 'R', 'RBI', 'SB')
raw_weights_hitting <- create_weights_df(
  c(rate_stats_hitting, counting_stats_hitting),
  c(1, 1, 1, 1, 1, 1.3)
)
