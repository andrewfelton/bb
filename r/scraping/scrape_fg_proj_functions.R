
dl_projections <- function(type, system, mytype, mysystem) {
  
  
  fg_proj_url_base = 'https://www.fangraphs.com/projections.aspx?pos=all'
  fg_proj_url_type = paste0('stats=',type)
  fg_proj_url_system = paste0('type=',system)
  
  fg_proj_url = paste(fg_proj_url_base, fg_proj_url_type, fg_proj_url_system, sep="&")
  
  remDr$navigate(fg_proj_url)
  Sys.sleep(5)
  account_text <- remDr$findElement(using = "id", value = "linkAccount")
  login_name <- account_text$getElementText()
  stopifnot(login_name[[1]]=="JohnnyFang")
  
  
  dl <- remDr$findElement(using="id", value = "ProjectionBoard1_cmdCSV")
  ret <- dl$clickElement()
  Sys.sleep(2)
  
  # copy the file from the Docker container to local machine
  system2(
    command = "docker",
    args <- paste(
      "cp",
      paste0(docker_id_ff,":/home/seluser/Downloads/FanGraphs\\ Leaderboard.csv"),
      "/Users/andrewfelton/Downloads/",
      sep = " "
    ),
    stdout=TRUE
  )
  
  # remove the file on the Docker container
  system2(
    command = "docker",
    args <- paste(
      "exec",
      docker_id_ff,
      "rm -rf",
      "/home/seluser/Downloads/FanGraphs\\ Leaderboard.csv",
      sep = " "
    ),
    stdout=TRUE
  )
  
  
  
  
  dl_file = "/Users/andrewfelton/Downloads/FanGraphs\\ Leaderboard.csv"
  today <- as.character(format(Sys.time(), "%Y%m%d"))
  new_file <- paste0(basepath, "/data/", mysystem, "_", mytype, "_", today, ".csv")
  system2(
    command = "mv",
    args <- paste(dl_file, new_file, sep = " ")
  )
  
  
  ln_file <- paste0(basepath, "/data/", mysystem, "_", mytype, ".csv")
  system2(
    command = "ln",
    args <- paste("-sf", new_file, ln_file, sep = " ")
  )
  
}
