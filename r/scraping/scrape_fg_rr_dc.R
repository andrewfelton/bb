

library(RSelenium)
library(XML)

system2(command="docker", 
        args="run -d -p 4445:4444 selenium/standalone-firefox")

remDr <- remoteDriver(port = 4445L)
remDr$open()

dc_url = 'https://www.fangraphs.com/roster-resource/depth-charts/'
team = 'yankees'
team = 'blue-jays'

remDr$navigate(paste0(dc_url, team))
Sys.sleep(5)

xpath <- "/html/body/div[1]/div[2]/div/div[3]/div[3]/div/div/div/div[1]/table"
maintable <- remDr$findElement(using="xpath", xpath)

t_node <- (
  remDr$getPageSource()[[1]] %>% 
  read_html() %>%
  html_nodes(xpath=xpath)
  )

t_tr <- html_nodes(t_node, "tr")

t_nodes2 <- t_tr
t_nodes2[[1]] <- NULL
t_nodes2[[1]] <- NULL

t_nodes2 %>% html_table()


#maintable_chr <- unlist(strsplit(maintable$getElementText()[[1]], "\n"))
#maintable_chr[[5]]




tablerows <- maintable %>% findElementFromElement(using="tag name", value="tr")

tablerows <- maintable$findElements(using="tag name", value="tr")

tablehtml <- maintable$getElementAttribute("outerHTML")

html_table()


doc <- htmlParse(remDr$getPageSource()[[1]])
readHTMLTable(doc)



remDr$close()

