





#df = combined_hitters

#fg_dc_hitters = fg_dc_hitters[which(fg_dc_hitters$PA >= 350),]
calc_zar <- function(df) {
  print(deparse(substitute(df)))
  df$sample = (df$PA >= 500)
  for (i in 1:3) {
    df = calc_z_scores(
      df, 
      rate_stats = c('OBP', 'OPS'),
      counting_stats = c('HR', 'R', 'RBI', 'SB'),
      denom_stat = 'PA',
      weights = raw_weights_hitting
    )
    df$sample = (df$ZAR >= 0)
  }
  df = arrange(df, desc(ZAR.Wgt))
  return(df)
}

combined_hitters <- calc_zar(combined_hitters)


#dfs = list(fg_dc_hitters, pod_hitters)
#temp = dfs[[1]]


