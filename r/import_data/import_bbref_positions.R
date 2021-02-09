bbref_positions <- import_bbref(paste(basepath, '/data/bbref_fielding_appearances_2020.csv', sep=""))


bbref_positions$elig = " "
positions <- c('C', 'X1B', 'X2B', 'X3B', 'SS', 'OF')
positions_elig = c()

# check for eligibilty between two different thresholds
# bbref_positions_inbetween['inbetween'] = FALSE

for (pos in positions) {
  poselig = paste('Elig.', pos, sep="")
  positions_elig <- c(positions_elig, poselig)
  bbref_positions[poselig] <- lapply(bbref_positions[pos], 
                                     function(x) ifelse(x>=10,pos,""))

# TO CHECK FOR "IN BETWEEN" TWO THRESHOLDS
#  bbref_positions_inbetween['inbetween'] = 
#    bbref_positions_inbetween['inbetween'] |
#    (bbref_positions_inbetween[pos]>=5 & bbref_positions_inbetween[pos]<7)
}

bbref_positions['elig'] <- unite(bbref_positions[,all_of(positions_elig)], 'elig', sep=' ')
pos_eligibility <- bbref_positions %>% select(name, bbref_id, fg_id, elig, all_of(positions_elig))
pos_eligibility$elig <- str_squish(pos_eligibility$elig)
pos_eligibility$elig <- ifelse(pos_eligibility$elig=="","UT",pos_eligibility$elig)



