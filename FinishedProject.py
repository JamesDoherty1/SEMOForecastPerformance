import requests  # API requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET  # Will be used to parse the data
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import pytz
from IPython.display import display

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"

def apiQuery(parameters):
    Response = requests.get(api_link, params=parameters)
    return Response

# Specifying our parameters
startDate = '2024-05-04'
endDate = '2024-07-03'
PageSize = '1'
SortBy = 'PublishTime'
ForecastReportName = 'Forecast Availability'
OutturnReportName = 'Average Outturn Availability'
ParticipantNameROI = 'PT_400116'
ParticipantNameNI = 'PT_502516'

ResourceNames = {"EE1":"DSU_401400", "EE2":"DSU_401870", "EE3":"DSU_402100", "EE4":"DSU_402120", "EE5":"DSU_402090", "EE6":"DSU_403520",
"EE7":"DSU_403560", "EE8":"DSU_403630", "EE9": "DSU_403640","VN1":"DSU_503460", "VS1":"DSU_403730","VS2": "DSU_403760"  }
#VN1 is empty , ,
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
            XMLFileNames.extend(FilteredGridInfo)  # Extend instead of append

            #print("\n\n\n" + XMLFileType + ":", FilteredGridInfo)

    return XMLFileNames



ForecastResponseData = RetrieveXMLFileNames(ForecastReportName)
OutturnResponseData = RetrieveXMLFileNames(OutturnReportName)

#Funtion to pass in the names we gathered and doing a api query to get the XML files content into a dataframe
def ResponseDataToDataFrame(ResponseData, Availability, ParticipantNameROI, ParticipantNameNI):
    availability_array = []
    data_array = []
    ResourceNames = []
    for data in ResponseData:
        url = 'https://reports.sem-o.com/documents/' + data
        df = pd.read_xml(url)

        if 'ParticipantName' in df.columns and Availability in df.columns:
            filtered_dfROI = df[df['ParticipantName'] == ParticipantNameROI]
            filtered_dfNI = df[df['ParticipantName'] == ParticipantNameNI]
            filtered_df = pd.concat([filtered_dfROI, filtered_dfNI])
            availability_array.extend(filtered_df[Availability].dropna().tolist())
            data_array.extend(filtered_df['StartTime'].dropna().tolist())
            ResourceNames.extend(filtered_df['ResourceName'].dropna().tolist())

    data = {'Times': data_array, 'Availability': availability_array, 'ResourceName': ResourceNames}
    df = pd.DataFrame(data=data)
    return df



Forecast = ResponseDataToDataFrame(ForecastResponseData, 'ForecastAvailability', ParticipantNameROI,ParticipantNameNI)
Outturn = ResponseDataToDataFrame(OutturnResponseData, 'AvgOutturnAvail', ParticipantNameROI, ParticipantNameNI)


#changing string to date and time
Forecast['Times'] = pd.to_datetime(Forecast['Times'])
Outturn['Times'] = pd.to_datetime(Outturn['Times'])

#changing forecast fromt UTC to Irish Time
Forecast['Times'] = Forecast['Times'] + pd.DateOffset(hours=1)

#formatted dates for the graph
full_time_range = pd.date_range(start=min(Forecast['Times'].min(), Outturn['Times'].min()),
                                end=max(Forecast['Times'].max(), Outturn['Times'].max()),
                                freq='30T')

print(Forecast)
print(Outturn)
#Averaging out the data points for any given time
# Forecast = Forecast.groupby('Times').mean().reindex(full_time_range).reset_index()
# Outturn = Outturn.groupby('Times').mean().reindex(full_time_range).reset_index()


for Resource in ResourceNames:
  print(Resource)
  ForecastNew = Forecast[Forecast['ResourceName']==ResourceNames[Resource]]
  OutturnNew = Outturn[Outturn['ResourceName']==ResourceNames[Resource]]


  plt.figure(figsize=(30, 6))

  plt.figure

  plt.plot(ForecastNew['Times'], ForecastNew['Availability'], label='Forecast')
  plt.plot(OutturnNew["Times"], OutturnNew['Availability'], label='Outturn')
  plt.xticks(rotation=90)
  plt.rcParams.update({'font.size':22})
  plt.legend()
  plt.xlabel('Times')
  plt.ylabel('Availability')
  plt.title(Resource)
  plt.show()

  #Same as above but using a scatterplot
for Resource in ResourceNames:
  print(Resource)
  ForecastNew = Forecast[Forecast['ResourceName']==ResourceNames[Resource]]
  OutturnNew = Outturn[Outturn['ResourceName']==ResourceNames[Resource]]


  plt.figure(figsize=(30, 10))
  plt.scatter(ForecastNew['Times'], ForecastNew['Availability'], label='Forecast',s=15)
  plt.scatter(OutturnNew['Times'], OutturnNew['Availability'], label='Outturn', s=15)
  plt.xticks(rotation=90)
  plt.rcParams.update({'font.size':22})
  plt.legend()
  plt.xlabel('Times')
  plt.ylabel('Availability')
  plt.title(Resource)
  plt.show()



for Resource in ResourceNames:
  print(Resource)
  ForecastNew = Forecast[Forecast['ResourceName']==ResourceNames[Resource]]
  OutturnNew = Outturn[Outturn['ResourceName']==ResourceNames[Resource]]


  labels = ['Average Outturn', 'Forecast Availibility']

  counts = [OutturnNew['Availability'].mean(),ForecastNew['Availability'].mean()]
  bar_labels = [ 'Forecast','Outturn']
  bar_colors = ['tab:blue','tab:orange']
  plt.figure(figsize=(10,10))
  plt.bar(labels, counts, label=bar_labels, color=bar_colors)


  plt.ylabel('Availability (MW)')
  plt.title(Resource)
  plt.legend(title='Viotas Outturn vs Availability')

  plt.show()


#using the keys as the X
names = ResourceNames.keys()
resource_names = np.unique(Forecast['ResourceName'])
x_axis = np.arange(len(resource_names))

forecast_means = Forecast.groupby('ResourceName')['Availability'].mean()
outturn_means = Outturn.groupby('ResourceName')['Availability'].mean()

plt.figure(figsize=(20, 10))
plt.bar(x_axis - 0.2, forecast_means, 0.4, label='Forecast')
plt.bar(x_axis + 0.2, outturn_means, 0.4, label='Outturn')

plt.xticks(x_axis, names, rotation=90)  # Rotate labels for readability
plt.xlabel("Resources")
plt.ylabel("Average Availability (MW)")
plt.title("Average Forecast vs Outturn Availability by Resource")
plt.legend()

# Display the chart
plt.tight_layout()  # Adjust layout for better spacing
plt.show()


all_weekly_forecast_mwh = pd.DataFrame()
all_weekly_outturn_mwh = pd.DataFrame()

#Breakdown
for Resource in ResourceNames:
  ForecastNew = Forecast[Forecast['ResourceName']==ResourceNames[Resource]].copy()
  OutturnNew = Outturn[Outturn['ResourceName']==ResourceNames[Resource]].copy()

  # halving the Availability do its MWh's
  ForecastNew['MWh'] = ForecastNew['Availability'] * 0.5
  OutturnNew['MWh'] = OutturnNew['Availability'] * 0.5

  #using pandas string to date funtion so we can use the dates funtionalitys
  ForecastNew['Times'] = pd.to_datetime(ForecastNew['Times'])
  OutturnNew['Times'] = pd.to_datetime(OutturnNew['Times'])

  #changing the dataframes inded to the time colums
  ForecastNew.set_index('Times', inplace=True)
  OutturnNew.set_index('Times', inplace=True)

  # Sampling the data weekly and setting it to start on the monday of each week
  weekly_forecast_mwh = ForecastNew['MWh'].resample('W-MON').sum()
  weekly_outturn_mwh = OutturnNew['MWh'].resample('W-MON').sum()

  all_weekly_forecast_mwh[Resource] = weekly_forecast_mwh
  all_weekly_outturn_mwh[Resource] = weekly_outturn_mwh

  plt.figure(figsize=(20, 12))
  plt.bar(weekly_forecast_mwh.index, weekly_forecast_mwh.values, label='Forecast MWh', width=2)
  plt.bar(weekly_outturn_mwh.index, weekly_outturn_mwh.values, label='Outturn MWh', width=2, align='edge')

  #only prints monday dates
  plt.xticks(weekly_forecast_mwh.index[weekly_forecast_mwh.index.dayofweek == 0],
           weekly_forecast_mwh.index[weekly_forecast_mwh.index.dayofweek == 0].strftime('%Y-%m-%d'),
           rotation=90)
  plt.xlabel('Week')
  plt.ylabel('MWh')
  plt.title(f'Weekly MWh for {Resource}')
  plt.legend()
  plt.tight_layout()
  plt.show()



# Sum the weekly MWh across all resources
total_weekly_forecast_mwh = all_weekly_forecast_mwh.sum(axis=1)
total_weekly_outturn_mwh = all_weekly_outturn_mwh.sum(axis=1)

#same plots as the individuals
plt.figure(figsize=(20, 12))
plt.bar(total_weekly_forecast_mwh.index, total_weekly_forecast_mwh.values, label='Total Forecast MWh', width=2)
plt.bar(total_weekly_outturn_mwh.index, total_weekly_outturn_mwh.values, label='Total Outturn MWh', width=2, align='edge')

plt.xticks(total_weekly_forecast_mwh.index[total_weekly_forecast_mwh.index.dayofweek == 0],
           total_weekly_forecast_mwh.index[total_weekly_forecast_mwh.index.dayofweek == 0].strftime('%Y-%m-%d'),
           rotation=90)
plt.xlabel('Week')
plt.ylabel('MWh')
plt.title('Total Weekly MWh: Outturn vs Availability')
plt.legend()
plt.tight_layout()
plt.show()



for i in range(len(forecast_means)):
  difference_forecast_outturn = forecast_means[i] - outturn_means[i]
  print(difference_forecast_outturn)

for key in ResourceNames.keys():
  average_difference_for_resource={

  }
  print(key)




def Summary_df(Forecast,Outturn):

  resource_summary = pd.DataFrame( columns = ['Name', 'Over Forecast', 'Under Forecast', 'Overall', 'Percentage Over', 'Percentage Under'])

  for Resource in ResourceNames:
    ForecastNew = Forecast[Forecast['ResourceName']==ResourceNames[Resource]]
    OutturnNew = Outturn[Outturn['ResourceName']==ResourceNames[Resource]]

    positive_diffs = []
    negative_diffs = []

    # Iterate through each row in OutturnNew
    for i in range(len(OutturnNew)):
      forecast_availability = ForecastNew['Availability'].iloc[i]
      outturn_availability = OutturnNew['Availability'].iloc[i]
      difference = forecast_availability - outturn_availability
      if difference == 0:
        positive_diffs.append(0)
        negative_diffs.append(0)
      elif difference >= 0:
        positive_diffs.append(difference)
      else:
        negative_diffs.append(difference)
  # Calculate the sums using the built-in sum() function
    positive = sum(positive_diffs)
    negative = sum(negative_diffs)
    total = sum(positive_diffs) + sum(negative_diffs)*(-1)
    posative_percentage = 0
    negative_percentage = 0

    if positive != 0 and negative ==0:
      posative_percentage = 100
      negative_percentage = 0
    elif positive == 0 and negative !=0:
      posative_percentage = 0
      negative_percentage = 100
    elif positive == 0 and negative ==0:
      posative_percentage = 50
      negative_percentage = 50
    else:
      posative_percentage = (positive/total)*100
      negative_percentage = (negative/total)*100


    new_row = [Resource, positive, negative, total, posative_percentage, negative_percentage]
    resource_summary.loc[len(resource_summary)] = new_row
  return resource_summary

OverallSummary = Summary_df(Forecast,Outturn)
print(OverallSummary)



def split_dataframe_weekly(df, time_column='Times'):

  # Ensure the time column is in datetime format
  df[time_column] = pd.to_datetime(df[time_column])

  # Set the time column as the index
  newdf = df.set_index(time_column, inplace=False)

  # Resample the DataFrame weekly, starting on Mondays
  weekly_dfs = {}
  current_week_start = newdf.index.min()
  next_sunday = current_week_start + pd.offsets.Week(weekday=6)

  while current_week_start <= newdf.index.max():
    week_end = min(next_sunday, newdf.index.max())  # End of week or end of DataFrame
    weekly_df = newdf[(newdf.index >= current_week_start) & (newdf.index <= week_end)]  # Include Sunday
    if not weekly_df.empty:
      weekly_dfs[current_week_start] = weekly_df

    current_week_start = next_sunday + pd.Timedelta(days=1) # Start of the next week (Monday)
    next_sunday += pd.offsets.Week()

  return weekly_dfs

Forecast_weekly = split_dataframe_weekly(Forecast)
Outturn_weekly = split_dataframe_weekly(Outturn)

display(Forecast_weekly)
display(Outturn_weekly)




for key in Forecast_weekly.keys():
  print(key)
  summary =Summary_df(Forecast_weekly[key], Outturn_weekly[key])
  display(summary)


  