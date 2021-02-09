
bbref_pitchers_2020 <- 
  import_bbref(paste(basepath, '/data/bbref_pitchers_2020.csv', sep=""))





bbref_pitchers_starters_2020 <- 
  import_bbref(paste(basepath, '/data/bbref_pitching_starting_2020.csv', sep=""))
bbref_pitchers_starters_2020$year <- 2020
bbref_pitchers_starters_2020$QS.PCT <- parse_number(bbref_pitchers_starters_2020$QS.)/100
bbref_pitchers_starters_2020 <- bbref_pitchers_starters_2020 %>%
  relocate(QS.PCT, .after=QS) %>%
  relocate(year, .after='fg_id')

bbref_pitchers_starters_2019 <- 
  import_bbref(paste(basepath, '/data/bbref_pitching_starting_2019.csv', sep=""))
bbref_pitchers_starters_2019$year <- 2019
bbref_pitchers_starters_2019$QS.PCT <- parse_number(bbref_pitchers_starters_2019$QS.)/100
bbref_pitchers_starters_2019 <- bbref_pitchers_starters_2019 %>%
  relocate(QS.PCT, .after=QS) %>%
  relocate(year, .after='fg_id')