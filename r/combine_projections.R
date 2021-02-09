
#comb_vars = c('HR.PA', 'RBI.PA', 'R.PA', 'SB.PA', 'OBP', 'OPS')
#proj_list = list('fg_dc_hitters', 'thebat_hitters')
#proj_weights = c(1, 1)
#denom_stat = 'PA'

#comb_vars = c('QS', 'SV', 'HLD', 'ERA', 'WHIP', 'SO')
#proj_list = list('fg_dc_pitchers', 'thebat_pitchers')
#proj_weights = c(1, 1)
#denom_stat = 'IP'




combine_projections <- function(comb_vars, proj_weights, proj_list, denom_stat) {
  for(i in 1:length(proj_list)) {
    #i <- 1
    weight = proj_weights[i]
    projdf <- eval(parse(text=proj_list[[i]]))
    
    if (i==1) {
      df = cbind(projdf[,c('fg_id', comb_vars)], weight)
    } else {
      df = rbind(df, cbind(projdf[,c('fg_id', comb_vars)], weight))
    }
  }
  
  # Arrange and group by fg_id of player
  df <- arrange(df, fg_id)
  group_by(df, fg_id)
  
  
  # sum up the weights
  weight_sums <-aggregate(
    df[c('weight')],
    by=list(df$fg_id), 
    FUN=sum, 
    na.rm=TRUE
  )
  weight_sums = rename(weight_sums, fg_id = Group.1)
  weight_sums = rename(weight_sums, weight.sum = weight)
  
  # Merge in the weight sums
  df = left_join(df, weight_sums, 'fg_id')
  
  
  # multiply each column in comb_vars by weight
  df = cbind(
    df[c('fg_id')],
    sapply(
      df[c(comb_vars)], 
      function(x) {
        as.numeric(x * df$weight / df$weight.sum)
      } 
    )
  )
  
  # sum the metrics
  df <-aggregate(
    df[comb_vars],
    by=list(df$fg_id), 
    FUN=sum, 
    na.rm=TRUE
  )
  df = rename(df, fg_id = Group.1)
  
  
  
  # Add the sums in
  if (denom_stat=='PA') {
    df = left_join(
      df,
      fg_dc_hitters[c('fg_id', denom_stat)],
      'fg_id'
    )
  } else {
    df = left_join(
      df,
      fg_dc_pitchers[c('fg_id', denom_stat)],
      'fg_id'
    )
  }
  
  df = df[c('fg_id', denom_stat, comb_vars)]
  

  if (denom_stat=='PA') {
    # multiply each column in comb_vars by weight
    calc_totals_from_PA_ratios = function(df, varname) {
      varname_pa = paste(varname, '.PA', sep='')
      t = df[varname_pa] * df['PA']
      names(t)[names(t) == varname_pa] <- varname
      return(t)
    }
    
    
    for (var in comb_vars) {
      if (grepl('.PA', var)) {
        df = cbind(
          df,
          calc_totals_from_PA_ratios(
            df, 
            substr(var, 1, nchar(var)-3)
          )
        )
      }
    }
  }
  
  df <- df %>% 
    left_join(names[c('fg_id', 'Canonical')], by='fg_id') %>%
    relocate('Canonical') %>%
    left_join(pos_eligibility[c('fg_id', 'elig')], by='fg_id') %>%
    relocate(c('elig'), .after=fg_id)
    
  
  return(df)
}



