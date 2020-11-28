#%% 
import os
import pandas as pd
import re
import sys
from datetime import datetime


# %%
station_id = "08353000"
target_date = "2020-11-01"


# reads USGS daily means csv and preserves the text nature of the site_no
def read_usgs_daily_means_csv(file_path):
    daily_means = pd.read_csv(file_path, dtype = object)
    daily_means = daily_means.astype({"month_nu": 'int32', 
                                      "day_nu": "int32", 
                                      "begin_yr": "int32", 
                                      "end_yr": "int32", 
                                      "count_nu": "int32", 
                                      "mean_va": "float64"})
    return(daily_means)

# station_id is a USGS ID, string type
# target date is in format "YYYY-MM-DD"
# file_path is the path to the csv file assumed to contain the daily means 
#    for the given station_id
# args_dict expects a dictionary with a key of "file_path" that leads to an actual file path
def forecast_daily_means(station_id, target_date, args_dict):
    # get data needed to make forecast
    # daily_means = get_daily_means(station_id = station_id, 
    #                               start_date = target_date, 
    #                               end_date = target_date + 10 days)
    if "file_path" not in args_dict.keys():
        raise NameError("file_path does not exist in args_dict")

    daily_means = read_usgs_daily_means_csv(args_dict["file_path"])
    station_means = daily_means.loc[daily_means["site_no"] == station_id]
    station_means = station_means.astype({"mean_va": int})

    if len(station_means.index) == 0:
        raise ValueError(f"station_id {station_id} doesn't exist in your daily means csv")
    
    # predict streamflow using data
    predict_df = pd.DataFrame(data = {"date_time": pd.Series(pd.date_range(start = target_date, periods = 11*4, freq = "6H"))})
    predict_df["month_nu"] = predict_df["date_time"].dt.month
    predict_df["day_nu"] = predict_df["date_time"].dt.day
    predict_df["station_id"] = station_id
    predict_df = predict_df.merge(station_means, how = "inner", left_on = ["month_nu", "day_nu"], right_on = ["month_nu", "day_nu"])

    predict_df = predict_df[["date_time", "station_id", "mean_va"]]
    predict_df = predict_df.rename(columns = {"site_no":"station_id", "mean_va":"value"})
    return(predict_df)


# station_id is a usgs ID, string type
# target date is a datetime object with a year, month, and a day.
# forecast function is the function used to create the forecast. It 
#  1. gets the data it needs, 
#  2. makes a prediction for the next 10 days, and 
#  3. returns that prediction as a pandas dataframe that is guaranteed to have the following columns:
#     -  date_time, as a pandas datetime dtype
#     -  station_id, the USGS station ID, as a pandas object dtype
#     -  value, the discharge in cfs
# the dataframe is guaranteed to have values at hours 0, 6, 12, and 18, but may have more. 
# forecast_args is a dictionary of named arguments for the forecasting function
# my_forecast = forecast(station_id, target_date, forecast_daily_means, {"file_path": "../data/daily_means.csv"})
def forecast(station_id, target_date, forecast_func, forecast_args):

    forecast_df = forecast_func(station_id, target_date, args_dict = forecast_args)

    # create df of streamflow forecast in correct format
    target_date = target_date.replace(hour = 18)
    needed_times = pd.Series(pd.date_range(start = target_date, periods = 10*4, freq = "6H"))

    if needed_times.isin(forecast_df["date_time"]).all() == False:
        raise RuntimeError("Your forecast function didn't provide all the needed datetimes. Got this df: \n", forecast_df)
    else:
        forecast_df = forecast_df.loc[forecast_df["date_time"].isin(needed_times) == True]

    codemap = {
        "08353000" : "BNDN5",
        "06468250" : "ARWN8",
        "11523200" : "TCCC1",
        "07301500" : "CARO2",
        "06733000" : "ESSC2", "BTABESCO" : "ESSC2", # USGS only has data through 1998
        "11427000" : "NFDC1",
        "09209400" : "LABW4",
        "06847900" : "CLNK1",
        "09107000" : "TRAC2",
        "06279940" : "NFSW4"
    }

    forecast_df["DateTime"] = forecast_df["date_time"].dt.strftime("%Y-%m-%dT%H")
    forecast_df["LocationID"] = forecast_df["station_id"].map(codemap)
    forecast_time = target_date.replace(hour = 0)
    forecast_df["ForecastTime"] = forecast_time.strftime("%Y-%m-%dT%H")
    forecast_df["VendorID"] = "TC+tbadams45"
    forecast_df["Value"] = forecast_df["value"]
    forecast_df["Units"] = "CFS"

    
    # return df with correctly formatted streamflow forecast
    return(forecast_df[["DateTime", "LocationID", "ForecastTime", "VendorID", "Value", "Units"]])


def forecast_all_test_stations(target_date, forecast_func, forecast_args):
    station_ids = {
        "08353000" : "BNDN5",
        "06468250" : "ARWN8",
        "11523200" : "TCCC1",
        "07301500" : "CARO2",
        "06733000" : "ESSC2", # "BTABESCO" : "ESSC2", # USGS only has data through 1998
        "11427000" : "NFDC1",
        "09209400" : "LABW4",
        "06847900" : "CLNK1",
        "09107000" : "TRAC2",
        "06279940" : "NFSW4"
    }

    final_df = pd.DataFrame(data = {"DateTime": '',
                                    "LocationID": '',
                                    "ForecastTime":'',
                                    "VendorID":'',
                                    "Value":int(),
                                    "Units":''}, index = [])
    for station_id in list(station_ids.keys()):
        forecast_df = forecast(station_id, target_date, forecast_func, forecast_args)
        final_df = final_df.append(forecast_df, ignore_index = True)

    return final_df

def write_forecast_file(forecast, file_path):
    forecast.to_csv(path_or_buf = file_path, index = False)
# %%

def main(argv):
    year  = argv[0][0:4]
    month = argv[0][5:7]
    day   = argv[0][8:]
    target_date = datetime(int(year),int(month), int(day))
    forecast_df = forecast_all_test_stations(target_date, forecast_daily_means, {"file_path": "./daily_means.csv"})
    write_forecast_file(forecast_df, argv[1])

if __name__ == '__main__':
    main(sys.argv[1:])