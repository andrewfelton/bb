

library(httr)
library(rvest)
library(dplyr)





res <- POST("https://www.fangraphs.com/projections.aspx?pos=all&stats=pit&type=fangraphsdc&team=0&lg=all&players=0",
            encode="form",
            user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.50 Safari/537.36"),
            add_headers('authority: www.fangraphs.com',
                        'cache-control: max-age=0',
                        'sec-ch-ua: "Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
                        'sec-ch-ua-mobile: ?0',
                        'upgrade-insecure-requests: 1',
                        'origin: https://www.fangraphs.com',
                        'content-type: application/x-www-form-urlencoded',
                        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'sec-fetch-site: same-origin',
                        'sec-fetch-mode: navigate',
                        'sec-fetch-user: ?1',
                        'sec-fetch-dest: document',
                        'referer: https://www.fangraphs.com/projections.aspx?pos=all&stats=pit&type=fangraphsdc&team=0&lg=all&players=0',
                        'accept-language: en-US,en;q=0.9'
                        )
)



res_t <- content(res, as="text")



write.csv(res_t, "~/Documents/bb/2021/data/fg_scrape_output.csv")
