
names <- as.data.frame(read_sheet(gs, sheet = "Names"), stringsAsFactors=FALSE) 


# This is the data set with the list of names to import
import_list <- read.csv()



# Add new names onto the bottom

names_base <- names[c('Canonical', 'bbref_id')]

# 






fg_names <- steamer_batters[,c("name","fg_id")]
bbref_names <- bbref_batters[,c("name", "bbref_id")]

# Use Steamer as the base
names <- merge(bbref_names, steamer_names, by.x="name", by.y="name", all.x = FALSE, all.y = TRUE)


missing_bbref <- subset(names, is.na(bbref_id))
missing_bbref <- merge(missing_bbref, bbref_names, by.x=NULL, by.y=NULL)

missing_bbref$name.x <- gsub('\\.', '', missing_bbref$name.x)
missing_bbref$name.y <- gsub('\\.', '', missing_bbref$name.y)



missing_bbref$dist = stringdist(tolower(missing_bbref$name.x),tolower(missing_bbref$name.y),method = 'osa')
missing_bbref <- subset(missing_bbref, dist<2)
missing_bbref <- missing_bbref[
  with(missing_bbref, order(name.x, dist)),
]




write.csv(names, "~/Documents/bb/2021/data/names.csv")
write.csv(missing_bbref, "~/Documents/bb/2021/data/missing_bbref.csv")



