#df <- fg_dc_pitchers
#df <- combined_pitchers
calc_z_pitchers <- function(df, budget_split=.5) {
  if(!"sample" %in% colnames(df))
  {
    df$sample = (
      df$IP >= 150 | df$SVHLD >= 10
    )
  }
  
  
  for (i in 1:3) {
    df = calc_z_scores(
      df, 
      rate_stats = rate_stats_pitching,
      counting_stats = counting_stats_pitching,
      denom_stat = 'IP',
      weights = raw_weights_pitching,
      budget_split=budget_split
    )
    df$sample = (df$ZAR>0)
  }
  
  df = arrange(df, desc(Z.Wgt))
  df <- df %>% select(-one_of(c('sample')))

  df['ZAR.Skills'] <- df['ERA.Z']+df['WHIP.Z']+df['SO.Z']
  
  if("SV" %in% colnames(df)) {
    df$elig <- ifelse(df$SV>10, 'CL',
                      ifelse(df$HLD>10, 'MR',
                             ifelse(df$QS>5, 'SP', 'P')))
    df <- df %>%
      group_by(Team) %>%
      mutate(
        closer = (SV == max(SV))
      ) %>%
      ungroup()
  } else {
    df$elig <- ifelse(df$SVHLD>10, 'RP',
                       ifelse(df$QS>5, 'SP', 'P'))
  }
  
  if (1==0) {
    rp <-
      df[c('fg_id','Team','GS','ZAR.Skills')] %>%
      filter(GS == 0) %>%
      filter(Team != '') %>%
      group_by(Team) %>%
      mutate(rp.rank = (rank(-ZAR.Skills))) %>%
      ungroup()
    df <- left_join(df, rp[c('fg_id', 'rp.rank')], by='fg_id')
    
    sp <-
      df[c('fg_id','Team','GS','ZAR.Wgt')] %>%
      filter(GS > 5) %>%
      mutate(sp.rank = (rank(-ZAR.Wgt)))
    df <- left_join(df, sp[c('fg_id', 'sp.rank')], by='fg_id')
  }
  return(df)
}



# df <- combined_hitters
calc_z_hitters <- function(df, budget_split=.5) {
  if(!"sample" %in% colnames(df))
  {
    df$sample = (df$PA >= 500)
  }
  for (i in 1:3) {
    df = calc_z_scores(
      df, 
      rate_stats = rate_stats_hitting,
      counting_stats = counting_stats_hitting,
      denom_stat = 'PA',
      weights = raw_weights_hitting,
      budget_split=budget_split
    )
    df$sample = (df$ZAR>0)
  }
  
  
  
  
  
  df = arrange(df, desc(ZAR.Wgt))
  df <- df %>% select(-one_of(c('sample')))
  return(df)
}

