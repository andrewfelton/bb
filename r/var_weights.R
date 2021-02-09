
# This creates a data frame with the var names and "raw" weights
create_weights_df <- function(vars, weights) {
  df <- data.frame(
    "raw" = weights,
    stringsAsFactors = FALSE
  )
  df = as.data.frame(transpose(df))
  colnames(df) = vars
  return(df)
}

# Take a set of raw weights and a list of variables and return so they are properly weighted and sum to 1
get_weights <- function(weights, vars) {
  #vars <- basevars
  varlist = intersect(colnames(weights), vars)
  df = weights[varlist]
  wgtsum = rowSums(df)
  df = df / wgtsum * length(varlist)
  colnames(df) = get_suffixed_names(colnames(df), "Wgt")
  return(df)
}





