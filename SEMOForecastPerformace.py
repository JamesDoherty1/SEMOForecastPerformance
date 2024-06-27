import requests
import pandas as pd

# Function to filter XML strings from a JSON object
def filterXMLStrings(json_data):
    try:
        items = json_data.get('items', [])
        filtered_strings = [item['ResourceName'] for item in items if item['ResourceName'].endswith('.xml')]
        return filtered_strings
    except KeyError:
        print("KeyError: The JSON object does not contain the expected keys.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Specifying our parameters
startDate = '2024-06-20'
endDate = '2024-06-26'
PageSize = '1'
SortBy = 'PublishTime'
ForecastReportName = 'Daily Load Forecast Summary'
OutturnReportName = 'Average Outturn Availability'

# Getting the range of dates
dateRange = pd.date_range(start=startDate, end=endDate).date

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"

# Creating arrays to hold our data
ForecastResponseData = []
OutturnResponseData = []

# Retrieving Daily load forecast Summary
for date in dateRange:
    ForecastParameters = {
        'ReportName': ForecastReportName,
        'Date': date,
        'page_size': PageSize,
        'sort_by': SortBy,
    }
    ForecastResponse = requests.get(api_link, params=ForecastParameters)
    if ForecastResponse.status_code != 200:
        print(f"Failed to retrieve data: {ForecastResponse.status_code}")
    else:
        ForecastGridInfo = ForecastResponse.json()
        ForecastResponseData.append(ForecastGridInfo)
        FilteredForecast = filterXMLStrings(ForecastGridInfo)
        print("\n\n\nForecast Grid Information:", FilteredForecast)

# Retrieving the Average Outturn Availability 
for date in dateRange:
    OutturnParameters = {
        'ReportName': OutturnReportName,
        'Date': date,
        'page_size': PageSize,
        'sort_by': SortBy
    }
    OutturnResponse = requests.get(api_link, params=OutturnParameters)
    if OutturnResponse.status_code != 200:
        print(f"Failed to retrieve data: {OutturnResponse.status_code}")
    else:
        OutturnGridInfo = OutturnResponse.json()
        OutturnResponseData.append(OutturnGridInfo)
        FilteredOutturn = filterXMLStrings(OutturnGridInfo)
        print("\n\n\nOutturn Grid Information:", FilteredOutturn)