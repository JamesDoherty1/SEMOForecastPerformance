import requests  # API requests
import pandas as pd
import xml.etree.ElementTree as ET  # Will be used to parse the data

# Link to connect to the API
api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"

def apiQuery(parameters):
    Response = requests.get(api_link, params=parameters)
    return Response

# Specifying our parameters
startDate = '2024-05-20'
endDate = '2024-05-26'
PageSize = '1'
SortBy = 'PublishTime'
ForecastReportName = 'Forecast Availability'
OutturnReportName = 'Average Outturn Availability'
ResourceName = ''
ParticipantName = 'PT_400116'

# Getting the range of dates
dateRange = pd.date_range(start=startDate, end=endDate).date

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

# Function to loop through dates and return all the XML file names we need
def RetrieveXMLFileNames(XMLFileType):
    XMLFileNames = []
    for date in dateRange:
        TypeParameters = {
            'ReportName': XMLFileType,
            'Date': date,
            'page_size': PageSize,
            'sort_by': SortBy,
        }
        Response = apiQuery(TypeParameters)
        if Response.status_code != 200:
            print(f"Failed to retrieve data: {Response.status_code}")
        else:
            GridInfo = Response.json()

            # Filtering data to isolate the names of the XML files we want to use
            FilteredGridInfo = filterXMLStrings(GridInfo)
            XMLFileNames.append(FilteredGridInfo)
            print("\n\n\n" + XMLFileType + ":", FilteredGridInfo)

    return XMLFileNames

ForecastResponseData = RetrieveXMLFileNames(ForecastReportName)
OutturnResponseData = RetrieveXMLFileNames(OutturnReportName)

# Function that takes in an XML file and parses for our desired resource
def XMLParsing(XMLfileName,XMLfile, ResourceName):
    ParsedXML = []
    
    try:
        tree = ET.ElementTree(XMLfileName)
        print('found file')
        root = tree.getroot()
        # print(root.tag)
        # print(root.attrib)
        # for elem in root.findall('.//'):
        #     if ResourceName in elem.tag:
        #         ParsedXML.append(elem.text)
                
    except ET.ParseError as e:
        print(f"ParseError: Failed to parse XML file: {e}")
    
    return ParsedXML

def XMLFileData(arrayOfXMLFileNames, ResourceName):
    ParsedXMLfileData = []

    for XMLfileName in arrayOfXMLFileNames:
        # Query for the file
        data = {
            'Name': XMLfileName
        }
        Response = apiQuery(data)
        if Response.status_code == 200:
            XMLFile = Response.text

            # Parse function to retrieve the resource
            ParsedXMLfileData.append(XMLParsing(XMLfileName,XMLFile, ResourceName))
    
    return ParsedXMLfileData

ParsedForecastData = XMLFileData(ForecastResponseData, "ForecastAvailability")
ParsedOutturnData = XMLFileData(OutturnResponseData, "AvgOutturnAvail")

print(ParsedForecastData)
print(ParsedOutturnData)