#csv_path = paste(basepath, '/data/bbref_qs_historical.csv', sep="")

import_bbref <- function(csv_path) {
  df <- read.csv(csv_path)
  if("Player" %in% colnames(df)) { 
    df <- df %>% rename(Name = Player) 
  }
  bbref_names <- as.data.frame(str_split_fixed(df$Name, "\\\\", 2))

  
  bbref_names$V1 <- str_replace(bbref_names$V1, "\\*", "")
  bbref_names$V1 <- str_replace(bbref_names$V1, "\\#", "")
  names(bbref_names) <- c('name', 'bbref_id')
  df <- cbind(df, bbref_names)
  
  df <- left_join(df, names[c('Canonical', 'bbref_id', 'fg_id')], by='bbref_id')
  
  df <- df %>% 
    select (-c('Name', 'Rk')) %>%
    relocate(c('Canonical', 'bbref_id', 'fg_id'))
  return(df)
}


import_fg <- function(csv_path) {
  df <- read.csv(csv_path, stringsAsFactors=FALSE) 
  df = df %>% 
    rename(fg_id = playerid, name=Name) %>% 
    relocate(fg_id, .after=name)
  return(df)
}


import_fg_batters <- function(csvpath) {
  df <- import_fg(csvpath)
  df$TB     <- df$SLG * df$AB
  df$TOB    <- df$OBP * df$PA
  df$HR.PA  <- df$HR  / df$PA
  df$RBI.PA <- df$RBI / df$PA
  df$R.PA   <- df$R   / df$PA
  df$SB.PA  <- df$SB  / df$PA
  return(df)
}


import_fg_pitchers <- function(csvpath) {
  df <- import_fg(csvpath)
  
  df$QS = ifelse(
    df$GS > 0,
    (df$GS / (df$ER * df$GS / df$G)) * 
      (df$IP * df$GS / df$G) * 
      ((df$GS+df$G)/(2*df$G))^2 /
      4.11556,
    0
  )
  # QS = GS / (ER * (GS/GP)) * (IP * (GS/GP)) * ((GS+GP)/(2*GP))^2
  # https://fantasybaseballcalculator.webs.com/quality-starts-predictor
  
  if("HLD" %in% colnames(df)) { 
    df['SVHLD'] = df['SV'] + df['HLD']
  }
  
  return(df)
}

