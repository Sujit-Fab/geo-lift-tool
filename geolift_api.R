library(plumber)
library(GeoLift)

#* @apiTitle GeoLift API
#* @post /geolift
function(req) {
  data <- read.csv(req$body$data_path)
  params <- req$body$params
  result <- GeoLiftMarketSelection(
    data = data,
    locations = unique(data$location),
    treatment_periods = params$pre_test_weeks,
    holdout = params$holdout_percent / 100
  )
  return(list(
    groups = result$BestMarkets,
    historical_data = result$data,
    duration = result$duration,
    power = result$power
  ))
}