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
startDate = '2024-05-20'
endDate = '2024-05-26'
PageSize = '1'
SortBy = 'PublishTime'
ForecastReportName = 'Daily Load Forecast Summary'
OutturnReportName = 'Average Outturn Availability'

# Getting the range of dates
dateRange = pd.date_range(start=startDate, end=endDate).date

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"


def AppendingReportData(ReportName):
    ReportData=[]
    for date in dateRange:

        Parameters = {
            'ReportName': ReportName,
            'Date': date,
            'page_size': PageSize,
            'sort_by': SortBy
        }
        Response = requests.get(api_link, params=Parameters)
        if Response.status_code != 200:
            print(f"Failed to retrieve data: {Response.status_code}")
        else:
            GridInfo = Response.json()
            FilteredInfo = filterXMLStrings(GridInfo)
            ReportData.append(FilteredInfo)
            print("\n\n\n"+ReportName+': ', FilteredInfo)
    return ReportData

# Creating arrays to hold our data
ForecastResponseData = AppendingReportData(ForecastReportName)
OutturnResponseData = AppendingReportData(OutturnReportName)
