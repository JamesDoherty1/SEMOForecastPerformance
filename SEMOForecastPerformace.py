import requests
import pandas as pd

startDate = '2024-06-20'
endDate = '2024-06-26'
FileName = "PUB_DailyLoadFcst_202406260835.xml" #5 min period isolation example
PageSize = '10'
SortBy = 'PublishTime'
ForecastReportName = 'Daily Load Forecast Summary'
OutturnReportName = 'Average Outturn Availability'

dateRange = pd.date_range(start=startDate, end=endDate).date

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"

#Retriving Daily load forecast Summary
for date in dateRange:
     
     ForecastParameters = {
        'ReportName' : ForecastReportName,
        'Date': date,
        'page_size': PageSize,
        'sort_by': SortBy
    }
     ForecastResponse = requests.get(api_link, params=ForecastParameters)
     if ForecastResponse.status_code != 200:
        print(f"Failed to retrieve data: {ForecastResponse.status_code}")
         
     else:
        ForecastGridInfo = ForecastResponse.json()

        print("\n\n\nForecast Grid Information:", ForecastGridInfo)
         

#Retriving the Average Outturn Availability 
for date in dateRange:

    OutturnParameters = {
        'ReportName' : OutturnReportName,
        'Date': date,
        'page_size': PageSize,
        'sort_by': SortBy
    }
    OutturnResponse = requests.get(api_link, params=OutturnParameters)
    if OutturnResponse.status_code != 200:
        print(f"Failed to retrieve data: {OutturnResponse.status_code}")

    else:
        OutturnGridInfo = OutturnResponse.json()

        print("Forecast Grid Information:", ForecastGridInfo)
        print("\n\n\nOutturn Grid Information:", OutturnGridInfo)