if (1==0) {
  df <- combined_hitters
  comb_vars = c('HR.PA', 'RBI.PA', 'R.PA', 'SB.PA', 'OBP', 'OPS')
  system_list = list('fg_dc', 'thebat', 'thebatx')
  proj_weights = c(1, 1, 1)
  denom_stat = 'PA'
  type='hitters'
  
  df <- combined_pitchers
  comb_vars = c('QS', 'SV', 'HLD', 'ERA', 'WHIP', 'SO')
  type = 'pitchers'
  system_list = list('fg_dc', 'thebat')
  proj_weights = c(1, 1)
  denom_stat = 'IP'
}



combine_project_hitters <- function(df, comb_vars) {
  df = left_join(
    df,
    fg_dc_hitters[c('fg_id', 'PA', 'AB')],
    'fg_id'
  )
  
  
  # multiply each column in comb_vars by weight
  calc_totals_from_PA_ratios = function(df, varname) {
    varname_pa = paste(varname, '.PA', sep='')
    t = df[varname_pa] * df['PA']
    names(t)[names(t) == varname_pa] <- varname
    return(t)
  }
  
  for (var in comb_vars) {
    #var = 'HR.PA'
    if (grepl('.PA', var)) {
      df <- cbind(
        df,
        calc_totals_from_PA_ratios(
          df, 
          substr(var, 1, nchar(var)-3)
        )
      )
    }
  }

  return(df)
}


combine_project_pitchers <- function(df) {
  df = left_join(
    df,
    fg_dc_pitchers[c('fg_id', 'IP', 'Team')],
    'fg_id'
  )
  return(df)
}




combine_projections <- function(comb_vars, type, system_list, denom_stat) {
  for(system in system_list) {
    #system = 'thebat'
    weight = system_weights[[type]][[system]]
    projdf <- eval(parse(text=paste(system, "_", type, sep="")))
    
    if (system==system_list[[1]]) {
      df = cbind(projdf[c('fg_id', comb_vars)], weight)
    } else {
      df = rbind(df, cbind(projdf[,c('fg_id', comb_vars)], weight))
    }
  }
  
  # Arrange and group by fg_id of player
  df <- df %>% 
        arrange(fg_id) %>%
        group_by(fg_id)
  
  # sum up the weights
  df <- df %>% mutate(weight.sum = sum(weight))

  # multiply each column in comb_vars by weight
  df2 <- data.frame(sapply(
    df[c(comb_vars)],
    function(x) {
      as.numeric(x * df$weight / df$weight.sum)
    } 
  ))
  df <- cbind(data.frame(df[c('fg_id')]), df2)

  
  # sum the metrics
  df <-aggregate(
         df[comb_vars],
         by=list(df$fg_id), 
         FUN=sum, 
         na.rm=TRUE
       ) %>% 
       rename(fg_id = Group.1)
  
  
  
  # Add the sums in
  if (type=='hitters') {
    df <- combine_project_hitters(df, comb_vars)
    denom_stats = c('PA', 'AB')
  } else {
    df <- combine_project_pitchers(df)
    denom_stats = c('IP')
  }
#  df = df[c('fg_id', denom_stats, comb_vars)]
  
  # Add in the canonical names and position eligibilities
  df <- df %>% 
    left_join(names[c('fg_id', 'Canonical')], by='fg_id') %>%
    relocate('Canonical') %>%
    left_join(pos_eligibility[c('fg_id', 'elig')], by='fg_id') %>%
    relocate(c('elig'), .after=fg_id)
    
  
  return(df)
}



