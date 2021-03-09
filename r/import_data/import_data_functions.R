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
  
  if (1==0) {
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
  }
  
  if("HLD" %in% colnames(df)) { 
    df['SVHLD'] = df['SV'] + df['HLD']
  }
  
  return(df)
}




import_cm <- function(csv_path) {
  #  csv_path = paste(basepath, '/data/couchmanagers/couchmanagers.csv', sep="")
  df <- read.csv(csv_path)
  df['Type'] = ifelse(df['Pos']=='SP' | df['Pos']=='RP','P','B')

  cm_names = names
  cm_names['CouchManagers'][is.na(cm_names['CouchManagers'])] <- cm_names['Canonical'][is.na(cm_names['CouchManagers'])]

  df <- left_join(df, 
              cm_names[c('CouchManagers', 'fg_id')] %>% rename(Player = CouchManagers),
              by='Player'
  )
  
  df <- subset(df, fg_id!='NA')

  
  df <- left_join(df,
                  names[c('Canonical', 'fg_id')], 
                  by='fg_id') 
  
  df <- left_join(df,
                  pos_eligibility[c('fg_id', 'elig')], 
                  by='fg_id'
                  ) %>%
        relocate(c('elig'), .after=fg_id)
  return(df)
}


import_cm_hitters <- function(csv_path) {
  df <- import_cm(csv_path)
  df <- subset(df, Type!='P')
  df <- df %>% 
    select (-c('Player', 'Rank', 'ERA', 'WHIP', 'SO', 'QS', 'SV', 'HLD')) %>%
    relocate(c('Canonical', 'fg_id'))
  return(df)
}

import_cm_pitchers <- function(csv_path) {
  df <- import_cm(csv_path)
  df <- subset(df, Type=='P')
  df <- df %>% 
    select (-c('Player', 'Rank', "AB","R","HR","RBI","SB","OBP",'OPS')) %>%
    relocate(c('Canonical', 'fg_id'))
  return(df)
}
