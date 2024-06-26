import requests
import pandas as pd

startDate = '2024-06-20'
endDate = '2024-06-26'
FileName = "PUB_DailyLoadFcst_202406260835.xml" #5 min period isolation example
PageSize = '10'
SortBy = 'PublishTime'
ForecastReportName = 'Daily Load Forecast Summary'
OutturnReportName = 'Average Outturn Availibility'

dateRange = pd.date_range(start=startDate, end=endDate)

for date in dateRange:

    ForecastParameters = {
        'ReportName' : ForecastReportName,
        'Date': date.date(),
        'page_size': PageSize,
        'sort_by': SortBy
    }

    OutturnParameters = {
        'ReportName' : OutturnReportName,
        'Date': date.date(),
        'page_size': PageSize,
        'sort_by': SortBy
    }
    api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"

    ForecastResponse = requests.get(api_link, params=ForecastParameters)
    OutturnResponse = requests.get(api_link, params=OutturnParameters)

    if ForecastResponse.status_code != 200:
        print(f"Failed to retrieve data: {ForecastResponse.status_code}")

    elif OutturnResponse.status_code != 200:
        print(f"Failed to retrieve data: {OutturnResponse.status_code}")

    else:
        ForecastGridInfo = ForecastResponse.json()
        OutturnGridInfo = OutturnResponse.json()

        print("Forecast Grid Information:", ForecastGridInfo)
        print("\n\n\nOutturn Grid Information:", OutturnGridInfo)




