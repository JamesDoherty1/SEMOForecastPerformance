import requests
import pandas as pd

#Specifying our parameters
startDate = '2024-06-20'
endDate = '2024-06-26'
FileName = "PUB_DailyLoadFcst_202406260835.xml" #5 min period isolation example
PageSize = '1'
SortBy = 'PublishTime'
ForecastReportName = 'Daily Load Forecast Summary'
OutturnReportName = 'Average Outturn Availability'

#Getting the range of dates
dateRange = pd.date_range(start=startDate, end=endDate).date

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"


#Creating arrays to hold out data
ForecastResponseData = []
OutturnResponseData = []

#Retriving Daily load forecast Summary
for date in dateRange:
     
     ForecastParameters = {
        'ReportName' : ForecastReportName,
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

        OutturnResponseData.append(OutturnGridInfo)
        print("\n\n\nOutturn Grid Information:", OutturnGridInfo)


def filter_xml_strings(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Ensure data is a list of strings
        if isinstance(data, list):
            filtered_strings = [s for s in data if isinstance(s, str) and s.endswith('.xml')]
            return filtered_strings
        else:
            print("The JSON file does not contain a list.")
            return []

    except json.JSONDecodeError:
        print("Failed to decode JSON.")
        return []
    except FileNotFoundError:
        print("File not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []