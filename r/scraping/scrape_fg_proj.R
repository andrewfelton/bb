

library(RSelenium)
library(XML)

# note: to debug, run the debut
# open VNC viewer
# password = 'secret'


docker_id_ff <- 
  system2(
    command = "docker",
    args <- paste(
      "run -d",
      "-p 4445:4444",
      "-p 5913:5900",
      "--user $(id -u):$(id -g)",
      "-v /Users/andrewfelton/Downloads:/Users/andrewfelton/Downloads",
#      "selenium/standalone-firefox",
      "selenium/standalone-firefox-debug",
      sep = " "
    ),
    stdout=TRUE
  )

Sys.sleep(5)

eCaps <- makeFirefoxProfile(list(
         browser.helperApps.neverAsk.saveToDisk = 
           "text/csv,text/plain,application/octet-stream,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         browser.download.manager.showWhenStarting = FALSE,
         browser.download.manager.closeWhenDone	= TRUE,
         browser.download.useDownloadDir = TRUE,
         browser.download.folderList = 2,
         browser.download.dir = '/Users/andrewfelton/Downloads'
         )
)

remDr <- remoteDriver(
  port = 4445L, 
  extraCapabilities = eCaps)
remDr$open()


#log in
remDr$navigate("https://blogs.fangraphs.com/wp-login.php")
username <- remDr$findElement(using = "id", value = "user_login")
username$sendKeysToElement(list("JohnnyFang"))
passwd <- remDr$findElement(using = "id", value = "user_pass")
passwd$sendKeysToElement(list("P1^nzGTY*Ew!r1"))
submit <- remDr$findElement(using = "id", value = "wp-submit")
submit$clickElement()
Sys.sleep(5)


dl_projections(type="bat", system="fangraphsdc", 
               mytype="batters",
               mysystem="fg_dc")
dl_projections(type="pit", system="fangraphsdc", 
               mytype="pitchers",
               mysystem="fg_dc")

dl_projections(type="bat", system="thebat", 
               mytype="batters",
               mysystem="thebat")
dl_projections(type="pit", system="thebat", 
               mytype="pitchers",
               mysystem="thebat")

dl_projections(type="bat", system="thebatx", 
               mytype="batters",
               mysystem="thebatx")



remDr$close()
system2(
  command = "docker",
  args <- paste("stop", docker_id_ff, sep = " ")
)

