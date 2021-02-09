
hitter_positions <- left_join(
  combined_hitters %>% select(!starts_with('elig')),
  bbref_positions,
  by='fg_id'
) %>% select(c('fg_id', '$.Wgt'), all_of(starts_with('Elig.')))

elig_positions <- colnames(hitter_positions %>% select(starts_with('Elig.')))

h2 <- hitter_positions
i = 3
for(pos in elig_positions) {
  h2[is.na(h2[pos]),i]<-""
  h2[h2[pos]!='',i]<-h2[h2[pos]!='',2]
  i = i+1
}

  
hitters_value_matrix <-
  pivot_longer(
    data = h2 %>% select(!c('$.Wgt')),
    cols = starts_with("Elig."),
    names_to = 'Elig',
    names_prefix = "Elig.",
    values_to = '$.Wgt'
    )
hitters_value_matrix['$.Wgt'] <- as.numeric(unlist(hitters_value_matrix['$.Wgt']))
hitters_value_matrix <- hitters_value_matrix[!is.na(hitters_value_matrix['$.Wgt']),]

sheet_write(hitters_value_matrix, gs, sheet = "Hitter $ Pos Matrix")

