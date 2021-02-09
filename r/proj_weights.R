

proj_weights_calc <- data.frame(
  "Starting" = c(1, 1, 1, 1, 1),
  "Ending" = c(1, 0, 0, 0, 1),
  "System" = c('fg_dc', 'pod', 'prof', 'pecota', 'thebat')
)

start_date = as.Date('2021-04-01')
end_date = as.Date('2021-10-03')

pct_left = max(min(as.double(end_date-Sys.Date( )) / as.double(end_date-start_date), 1), 0)
proj_weights_calc$Current = proj_weights_calc$Starting*pct_left + proj_weights_calc$Ending*(1-pct_left)
proj_weights_calc$Weight = proj_weights_calc$Current / sum(proj_weights_calc$Current)

rm(start_date, end_date, pct_left)


proj_weights <- setNames(as.list(proj_weights_calc$Current), proj_weights_calc$System)

