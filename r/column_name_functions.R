

get_suffixed_names <- function(colnames, suffix) {
  newnames = colnames
  for(i in 1:length(colnames)) {
    newnames[i] = paste(colnames[i], ".", suffix, sep='')
  }
  return(newnames)
}
