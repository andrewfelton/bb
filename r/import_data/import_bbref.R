library(tidyr)
library(stringr)
library(dplyr)
library(stringdist)


bbref_batters_2020 <- read.csv("~/Documents/bb/2021/data/bbref_batters_2020.csv", stringsAsFactors=FALSE)

bbref_batters <- bbref_batters_2020

# drop Rank
bbref_batters <- data.frame(bbref_batters %>% select(-Rk))

# Clean up the names
bbref_batters <- data.frame(bbref_batters %>% separate(Name, c("name", "bbref_id"), sep = "\\\\"))
bbref_batters$name <- str_replace(bbref_batters$name, '\\*', "")
bbref_batters$name <- str_replace(bbref_batters$name, '\\#', "")

# Filter to only have annual totals
num_obs <- data.frame(bbref_batters %>% count(name, sort=TRUE))
bbref_batters = merge(bbref_batters, num_obs, by="name") %>% subset(n==1 | Tm=='TOT') %>% select(-'n')
num_obs <- data.frame(bbref_batters %>% count(name, sort=TRUE))
bbref_batters = merge(bbref_batters, num_obs, by="name") %>% subset(n==1 | Lg=='MLB') %>% select(-'n')



rm(bbref_batters_2020, num_obs)