options(stringsAsFactors = FALSE)
#options(java.parameters = "-Xmx4g" )

library(rvest) 
#library(V8)
#library(baseballr)
#library(XLConnect)
library(tidyverse)
library(stringr)
library(data.table)
#library(purrr)
#library(curl)
#library(XML)
library(googlesheets4)

if (1==0) {
  settings = 'SoS'
  gs <- gs4_get('1-Cg_VSO5erkBg9YbtATX1uBfzwTiNpDi93UyD25uZkE')
  
  settings = 'Legacy'
  gs <- gs4_get('10YwNZpcsuXURz8sm34chdHDixD9l1y2-sGnOAVgg6-o')
}

basepath = '/Users/andrewfelton/Documents/bb/2021'
setwd(basepath)

source(paste(basepath, '/r/column_name_functions.R', sep=""))
source(paste(basepath, '/r/calc_z_scores.R', sep=""))
source(paste(basepath, '/r/calc_z.R', sep=""))
source(paste(basepath, '/r/combine_projections2.R', sep=""))
source(paste(basepath, '/r/proj_weights.R', sep=""))
source(paste(basepath, '/r/var_weights.R', sep=""))
source(paste(basepath, '/r/import_data/import_data_functions.R', sep=""))
source(paste(basepath, '/r/scraping/scrape_fg_proj_functions.R', sep=""))


# get the current list of names
names <- data.frame(read_sheet(gs, sheet = "Names"))
names$fg_id <- sapply(names$fg_id, paste, collapse='')

pt_override <- data.frame(read_sheet(gs, sheet = "PT Override"))



# set the z weights
source(paste0(basepath, '/r/set_league_settings.R'))



# set the system weights
source(paste0(basepath, '/r/set_system_weights.R'))


# get the position eligibility
source(paste0(basepath, '/r/import_data/import_bbref_positions.R'))

# create the function to calculate quality starts
source(paste0(basepath, '/r/analysis/quality_starts.R'))




# import the projections
# Couch Managers
#cm_hitters <- import_cm_hitters(paste(basepath, '/data/couchmanagers/couchmanagers.csv', sep=""))
#cm_pitchers <- import_cm_pitchers(paste(basepath, '/data/couchmanagers/couchmanagers.csv', sep=""))

# FanGraphs Depth Charts
fg_dc_hitters <- import_fg_batters(paste(basepath, '/data/fg_dc_batters.csv', sep=""))
fg_dc_hitters <- fg_dc_hitters[!duplicated(fg_dc_hitters['fg_id']), ]
fg_dc_pitchers <- import_fg_pitchers(paste(basepath, '/data/fg_dc_pitchers.csv', sep=""))
fg_dc_pitchers['QS'] <- predict_qs(fg_dc_pitchers)['QS']
fg_dc_pitchers <- fg_dc_pitchers[!duplicated(fg_dc_pitchers['fg_id']), ]

thebat_hitters <- import_fg_batters(paste(basepath, '/data/thebat_batters.csv', sep=""))
thebat_pitchers <- import_fg_pitchers(paste(basepath, '/data/thebat_pitchers.csv', sep=""))
thebat_pitchers['QS'] <- predict_qs(thebat_pitchers)['QS']
thebat_pitchers <- left_join(thebat_pitchers, fg_dc_pitchers[c('fg_id', 'SV', 'HLD')], by='fg_id') %>% 
  relocate(HLD, .after=SV.x)
thebat_pitchers['SV.x'] <- thebat_pitchers['SV.y']
thebat_pitchers <- thebat_pitchers %>% rename(SV=SV.x) %>% select(-c('SV.y'))
thebat_pitchers['SVHLD'] <- thebat_pitchers['SV'] + thebat_pitchers['HLD']
thebatx_hitters <- import_fg_batters(paste(basepath, '/data/thebatx_batters.csv', sep=""))

thebat_pitchers <- thebat_pitchers[is.na(thebat_pitchers[,'IP'])==FALSE,]




#pod_pitchers <- calc_z_pitchers(pod_pitchers)
#pod_hitters <- calc_z_hitters(pod_hitters)

fg_dc_hitters <- calc_z_hitters(fg_dc_hitters)
fg_dc_pitchers <- calc_z_pitchers(fg_dc_pitchers)

thebat_hitters <- calc_z_hitters(thebat_hitters)
thebat_pitchers <- calc_z_pitchers(thebat_pitchers)

thebatx_hitters <- calc_z_hitters(thebatx_hitters)

#pecota_pitchers <- calc_z_pitchers(pecota_pitchers)
#pecota_hitters <- calc_z_hitters(pecota_hitters)




hitter_split = .65
pitcher_split = 1-hitter_split

proj_list_hitters = c('fg_dc', 'thebat', 'thebatx')
combined_hitters <- combine_projections(comb_vars_hitters, 'hitters', proj_list_hitters, 'PA')
combined_hitters <- calc_z_hitters(combined_hitters['PA'>0], budget_split=hitter_split)

proj_list_pitchers = c('fg_dc', 'thebat')
combined_pitchers <- combine_projections(comb_vars_pitchers, 'pitchers', proj_list_pitchers, 'IP')
combined_pitchers['SVHLD'] = combined_pitchers['SV']+combined_pitchers['HLD']
if (1==0) {
  combined_pitchers <- left_join(combined_pitchers,
                                 fg_dc_pitchers[c('fg_id', 'Team')],
                                 by='fg_id') %>%
    relocate('Team', .after=fg_id) %>%
    left_join(pt_override[c('fg_id', 'IP_override', 'GS_override')], by='fg_id')
  combined_pitchers['IP'][!is.na(combined_pitchers['IP_override'])] <- 
    combined_pitchers['IP_override'][!is.na(combined_pitchers['IP_override'])]
  combined_pitchers['GS'][!is.na(combined_pitchers['GS_override'])] <- 
    combined_pitchers['GS_override'][!is.na(combined_pitchers['GS_override'])]
  combined_pitchers['IP_override'] <- NULL
  combined_pitchers['GS_override'] <- NULL
}
combined_pitchers <- calc_z_pitchers(combined_pitchers, budget_split=pitcher_split)



combined_all = union(
  cbind(combined_hitters[c('Canonical', 'fg_id', 'ZAR.Wgt', '$.Wgt')], data.frame('Type'=c('B'), stringsAsFactors=FALSE)),
  cbind(combined_pitchers[c('Canonical', 'fg_id', 'ZAR.Wgt', '$.Wgt')], data.frame('Type'=c('P'), stringsAsFactors=FALSE))
)
combined_all = arrange(combined_all, desc(ZAR.Wgt))


# Sum up the B/P ZAR projections for Ohtani and append him on to the bottom of combined_all
ohtani <- combined_all[which(combined_all['fg_id']=='19755'),]
ohtani['ZAR.Wgt'] <- sum(ohtani['ZAR.Wgt'])
ohtani['$.Wgt'] <- sum(ohtani['$.Wgt'])
ohtani['Type'] <- 'B/P'
ohtani <- head(ohtani,1)

combined_all <- union(
  combined_all[which(combined_all['fg_id']!='19755'),], # combined_all less the Ohtani rows
  ohtani # The new combined Ohtani row
)
combined_all = arrange(combined_all, desc(ZAR.Wgt))
rm(ohtani)



combined_all <- select(combined_all, 'Canonical', 'Type', everything())
sheet_write(combined_all, gs, sheet = "Combined Z")
sheet_write(combined_hitters, gs, sheet = "Hitter Projections")
sheet_write(combined_pitchers, gs, sheet = "Pitcher Projections")





if (1==0) {
  cm_hitters['PA'] <- 1
  cm_hitters['sample'] <- cm_hitters['AB']>500
  cm_hitters_z <- calc_z_hitters(cm_hitters['AB'>100], budget_split=hitter_split)
  
  cm_pitchers['IP'] <- 1
  cm_pitchers['GS'] <- 1
  cm_pitchers['sample'] <- (cm_pitchers['QS']>5 || cm_pitchers['SV']>10 || cm_pitchers['HLD']>10)
  cm_pitchers[is.na(cm_pitchers)] <- 0
  cm_pitchers_z <- calc_z_pitchers(cm_pitchers, budget_split=pitcher_split)
  
  
  cm_combined_all = union(
    cbind(cm_hitters_z[c('Canonical', 'fg_id', 'ZAR.Wgt', '$.Wgt')], data.frame('Type'=c('B'), stringsAsFactors=FALSE)),
    cbind(cm_pitchers_z[c('Canonical', 'fg_id', 'ZAR.Wgt', '$.Wgt')], data.frame('Type'=c('P'), stringsAsFactors=FALSE))
  )
  cm_combined_all = arrange(cm_combined_all, desc(ZAR.Wgt))
  cm_combined_all <- select(cm_combined_all, 'Canonical', 'Type', everything())
  sheet_write(cm_combined_all, gs, sheet = "Combined Z")
  sheet_write(cm_hitters_z, gs, sheet = "Hitter Projections")
  sheet_write(cm_pitchers_z, gs, sheet = "Pitcher Projections")
  
}

