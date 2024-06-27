import requests #API requests
import pandas as pd

import xml.etree.ElementTree as ET # Will be used to parse the data

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
startDate = '2024-05-20'
endDate = '2024-05-26'
PageSize = '1'
SortBy = 'PublishTime'
ForecastReportName = 'Daily Load Forecast Summary'
OutturnReportName = 'Average Outturn Availability'

# Getting the range of dates
dateRange = pd.date_range(start=startDate, end=endDate).date

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"


def RetriveXMLFileNames(XMLFileType):
    XMLFileNames = []
    for date in dateRange:
        TypeParameters = {
        'ReportName': XMLFileType,
        'Date': date,
        'page_size': PageSize,
        'sort_by': SortBy,
        }
        Response = requests.get(api_link, params=TypeParameters)
        if Response.status_code != 200:
            print(f"Failed to retrieve data: {Response.status_code}")
        else:
            GridInfo = Response.json()

            #filtering data to isolate the names of the xml files we want to use
            FilteredGridInfo = filterXMLStrings(GridInfo)
            XMLFileNames.append(FilteredGridInfo)
            print("\n\n\n"+XMLFileType+":", FilteredGridInfo)
    return XMLFileNames

ForecastReponseData = RetriveXMLFileNames(ForecastReportName)
OuttrunResponseData = RetriveXMLFileNames(OutturnReportName)