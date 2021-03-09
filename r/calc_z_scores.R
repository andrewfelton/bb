if (1==0) {
  df2 = fg_dc_hitters
  df2$sample = df2$PA>500
  df2 = df2[which(df$PA>100),]
  df = combined_hitters
  denom_stat = 'PA'
  df = fg_dc_hitters
  rate_stats = c('OBP', 'OPS')
  counting_stats = c('HR', 'R', 'RBI', 'SB')
  denom_stat = 'PA'
  weights = raw_weights_hitting
  budget_split=.5
  
  df = pod_pitchers
  df = combined_pitchers
  df['sample'] <- (df$IP>100) | df$SVHLD > 12
  rate_stats = rate_stats_pitching
  counting_stats = counting_stats_pitching
  denom_stat = 'IP'
  weights = raw_weights_pitching
  budget_split=.5
}


calc_z_scores <- function(df, rate_stats, counting_stats, denom_stat, weights, budget_split=.5) {

  
  basevars = c(rate_stats, counting_stats)
  
  if(!"sample" %in% colnames(df))
  {
    df$sample = TRUE
  }
  
  sample = df[
    which(df$sample == TRUE),
    names(df) %in% c(basevars, denom_stat)
  ]
  sample = sample[, c(basevars, denom_stat)]
  


  # get the means and sd for all fields in the sample dataframe
  dist_mean = as.data.frame(transpose(as.data.frame(apply(sample, 2, mean))))
  colnames(dist_mean) = c(basevars, c(denom_stat))

  dist_sd = as.data.frame(transpose(as.data.frame(apply(sample, 2, sd))))
  colnames(dist_sd) = c(basevars, c(denom_stat))
  
  # Create the .Z variables
  zvars = get_suffixed_names(basevars, "Z")
  df[zvars] = NA
  
  # Get the variable weights for the Z.Wgt calculation
  weights <- get_weights(weights, basevars)
  wgtvars <- get_suffixed_names(basevars, "Wgt")
  
  # Calculate a ratio for the denominator for the rate stats
  denomz = paste(denom_stat, '.Z', sep='')
  df[denomz] = (df[denom_stat] / as.numeric(dist_mean[denom_stat]))

  # Create and set Z, Z.Wgt to zero
  df$Z = 0
  df$Z.Wgt = 0
  
  #i <- 4
  for(i in 1:length(basevars)) {
    #print(i)
    var  = basevars[i]
    mean = as.numeric(dist_mean[var])
    sd   = as.numeric(dist_sd[var])
    wgt  = as.numeric(weights[wgtvars[i]])
    
    
    df[zvars[i]] = (df[var] - mean) / sd
    
    # Scale the rate stats by relative PA
    if(var %in% rate_stats) {
      df[zvars[i]] <- df[zvars[i]] * df[denomz]
    }
    if(var %in% c('ERA', 'WHIP')) {
      df[zvars[i]] <- -1 * df[zvars[i]]
    }
    
    df['Z'] = df['Z'] + df[zvars[i]]
    df['Z.Wgt'] = df['Z.Wgt'] + (df[zvars[i]] * wgt)
  }
  
  # Get the replacement-level Z score
  df['Rank']     = rank(-df['Z'], na.last = TRUE)
  df['Rank.Wgt'] = rank(-df['Z.Wgt'], na.last = TRUE)
  
  # Calc Z Above Replacement
  df['ZAR'] = df['Z'] -  as.numeric(df[which(df$Rank == (num_teams*12)),c('Z')])
  df['ZAR.Wgt'] = df['Z.Wgt'] -  as.numeric(df[which(df$Rank == (num_teams*12)),c('Z.Wgt')])
  
  # Get the replacement-level Z score for catchers
  if(!('elig' %in% colnames(df))) {
     df <- left_join(df, pos_eligibility[c('fg_id', 'elig')], by='fg_id')
  }
  if('PA' %in% colnames(df)) {
    df['Catcher'] <- ifelse(is.na(df['elig']), FALSE, sapply(df['elig'], function(elig) {str_detect(elig, 'C')}))
    catchers <- df[df['Catcher']==TRUE,]
    catchers['Rank'] <- rank(-catchers['Z'], na.last = TRUE)
    catchers['Rank.Wgt'] <- rank(-catchers['Z.Wgt'], na.last = TRUE)
    catchers['ZAR.C'] = catchers['Z'] - as.numeric(catchers[which(catchers$Rank == (num_teams)),c('Z')])  
    catchers['ZAR.Wgt.C'] = catchers['Z.Wgt'] - as.numeric(catchers[which(catchers$Rank == (num_teams)),c('Z.Wgt')])  
    
    df <- left_join(df, catchers[c('fg_id', 'ZAR.C', 'ZAR.Wgt.C')], by='fg_id')
    df['ZAR'] <- pmax(df['ZAR'],  df['ZAR.C'], na.rm = TRUE)
    df['ZAR.Wgt'] <- pmax(df['ZAR.Wgt'],  df['ZAR.Wgt.C'], na.rm = TRUE)
    
    df <- df %>% select(-one_of(c('sample', 'Rank', 'Rank.Wgt', 'Catcher', 'ZAR.C', 'ZAR.Wgt.C')))
  }
  
  df2 <- df %>% filter(ZAR.Wgt>0)
  sum_zar_wgt <- sum(df2['ZAR.Wgt'])
  
  df['$.Wgt'] <- lapply(df['ZAR.Wgt'], function(x) {16*260*budget_split*x/sum_zar_wgt})
  df = arrange(df, desc("$.Wgt"))
  
  return(df)
}


