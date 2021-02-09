
qs_historical <- import_bbref(paste(basepath, '/data/bbref_qs_historical.csv', sep=""))



# filter out the "openers
# https://stathead.com/tiny/RH6BI

qs_historical['qs.pct'] <- qs_historical['QS']/qs_historical['GS']

qs_lag <- qs_historical[c('fg_id', 'Year', 'qs.pct')]
qs_lag['Year'] <- qs_lag['Year']+1
qs_lag <- qs_lag %>% rename('qs.pct.lag1' = 'qs.pct')


qs_predict <- left_join(qs_historical[c('Canonical', 'Year', 'fg_id', 'qs.pct', 'ERA', 'FIP', 'GS')],
                        qs_lag,
                        by=c('fg_id', 'Year'))
qs_predict <- qs_predict[!is.na(qs_predict['fg_id']),]
qs_predict['qs.pct.lag1.sq'] <- qs_predict['qs.pct.lag1']**2
qs_predict['ERA.SQ'] <- qs_predict['ERA']**2
qs_predict['GS.2020'] <- qs_predict['GS'] * (qs_predict['Year']==2020)

qs_predict <- qs_predict %>% arrange(qs_predict, Canonical, Year)
qs_model <- lm(qs.pct ~ qs.pct.lag1 + qs.pct.lag1.sq + ERA + ERA.SQ + GS + GS.2020,
               data=qs_predict[qs_predict['Year']>2018,],
               weights=GS)
#summary(fit)
#qs_predict['qs.pct.pred'] <- predict(fit, newdata = qs_predict) 
#qs_predict['qs.pct.delta'] <- qs_predict['qs.pct.pred'] - qs_predict['qs.pct']
#qs_predict <- qs_predict %>% select(-one_of(c('qs.pct.lag1','qs.pct.lag1.sq','ERA.SQ','GS.2020')))



# predict combined_pitchers
predict_qs <- function(df) {
  df <- df[c('name','fg_id','GS','ERA')]
  df['Year'] <- 2021
  df <- left_join(
    df,
    qs_lag,
    by=c('fg_id', 'Year'))
  df['qs.pct.lag1'] <- data.frame(sapply(df['qs.pct.lag1'], function(x) {ifelse(is.na(x),.3,x)}))
  
  df['qs.pct.lag1.sq'] <- df['qs.pct.lag1']**2
  df['ERA.SQ'] <- df['ERA']**2
  df['GS.2020'] <- df['GS'] * (df['Year']==2020)
  df['qs.pct.pred'] <- predict(qs_model, newdata = df) 
  df['QS'] <- df['GS'] * df['qs.pct.pred']
  df <- df %>% select(one_of(c('fg_id', 'QS')))
}




