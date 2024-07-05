import requests  # API requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz

api_link = "http://reports.sem-o.com/api/v1/documents/static-reports"

def api_query(parameters):
    Response = requests.get(api_link, params=parameters)
    return Response

# Specifying our parameters
start_date = '2024-06-03'
end_date = '2024-06-03'
page_size = '1'
sort_by = 'PublishTime'
forecast_report_name = 'Forecast Availability'
outturn_report_name = 'Average Outturn Availability'
participant_name_ROI = 'PT_400116'
participant_name_NI = 'PT_502516'

resource_names = {
    "EE1": "DSU_401400", "EE2": "DSU_401870", "EE3": "DSU_402100", "EE4": "DSU_402120",
    "EE5": "DSU_402090", "EE6": "DSU_403520", "EE7": "DSU_403560", "EE8": "DSU_403630",
    "EE9": "DSU_403640", "VN1": "DSU_503460", "VS1": "DSU_403730", "VS2": "DSU_403760"
}
# Getting the range of dates
date_range = pd.date_range(start=start_date, end=end_date).date

# Function to filter XML strings from a JSON object
def filter_xml_strings(json_data):
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
def retrieve_xml_file_names(xml_file_type):
    xml_file_names = []

    for date in date_range:
        type_parameters = {
            'ReportName': xml_file_type,
            'Date': date,
            'page_size': page_size,
            'sort_by': sort_by,
        }

        Response = api_query(type_parameters)

        if Response.status_code != 200:
            print(f"Failed to retrieve data: {Response.status_code}")
        else:
            GridInfo = Response.json()
            # Filtering data to isolate the names of the XML files we want to use
            filtered_grid_info = filter_xml_strings(GridInfo)
            xml_file_names.extend(filtered_grid_info)  # Extend instead of append

    return xml_file_names

forecast_response_data = retrieve_xml_file_names(forecast_report_name)
outturn_response_data = retrieve_xml_file_names(outturn_report_name)

# Function to pass in the names we gathered and doing an API query to get the XML files content into a dataframe
def response_data_to_dataframe(response_data, availability, participant_name_ROI, participant_name_NI):
    availability_array = []
    data_array = []
    resource_names = []
    for data in response_data:
        url = 'https://reports.sem-o.com/documents/' + data
        df = pd.read_xml(url)

        if 'ParticipantName' in df.columns and availability in df.columns:
            filtered_dfROI = df[df['ParticipantName'] == participant_name_ROI]
            filtered_dfNI = df[df['ParticipantName'] == participant_name_NI]
            filtered_df = pd.concat([filtered_dfROI, filtered_dfNI])
            availability_array.extend(filtered_df[availability].dropna().tolist())
            data_array.extend(filtered_df['StartTime'].dropna().tolist())
            resource_names.extend(filtered_df['ResourceName'].dropna().tolist())

    data = {'Times': data_array, 'Availability': availability_array, 'ResourceName': resource_names}
    df = pd.DataFrame(data=data)
    return df

forecast = response_data_to_dataframe(forecast_response_data, 'ForecastAvailability', participant_name_ROI,participant_name_NI)
outturn = response_data_to_dataframe(outturn_response_data, 'AvgOutturnAvail', participant_name_ROI, participant_name_NI)

# Changing string to date and time
forecast['Times'] = pd.to_datetime(forecast['Times'])
outturn['Times'] = pd.to_datetime(outturn['Times'])

# Changing forecast from UTC to Irish Time
forecast['Times'] = forecast['Times'] + pd.DateOffset(hours=1)

# Formatted dates for the graph
full_time_range = pd.date_range(start=min(forecast['Times'].min(), outturn['Times'].min()),
                                end=max(forecast['Times'].max(), outturn['Times'].max()),
                                freq='30T')

# Plotting Forecast vs Outturn as Line Plots
for resource, resource_name in resource_names.items():
    forecast_new = forecast[forecast['ResourceName'] == resource_name]
    outturn_new = outturn[outturn['ResourceName'] == resource_name]

    plt.figure(figsize=(30, 6))
    plt.plot(forecast_new['Times'], forecast_new['Availability'], label='Forecast')
    plt.plot(outturn_new["Times"], outturn_new['Availability'], label='Outturn')
    plt.xticks(rotation=90)
    plt.rcParams.update({'font.size':22})
    plt.legend()
    plt.xlabel('Times')
    plt.ylabel('Availability')
    plt.title(resource)
    plt.savefig(f"availability_against_resource_{resource}_line.jpg")
    plt.close('all')

# Plotting Forecast vs Outturn as Scatter Plots
for resource, resource_name in resource_names.items():
    forecast_new = forecast[forecast['ResourceName'] == resource_name]
    outturn_new = outturn[outturn['ResourceName'] == resource_name]

    plt.figure(figsize=(30, 10))
    plt.scatter(forecast_new['Times'], forecast_new['Availability'], label='Forecast', s=15)
    plt.scatter(outturn_new['Times'], outturn_new['Availability'], label='Outturn', s=15)
    plt.xticks(rotation=90)
    plt.rcParams.update({'font.size':22})
    plt.legend()
    plt.xlabel('Times')
    plt.ylabel('Availability')
    plt.title(resource)
    plt.savefig(f"availability_against_resource_{resource}_scatter.jpg")
    plt.close('all')

# Plotting Forecast vs Outturn as Bar Charts
for resource, resource_name in resource_names.items():
    forecast_new = forecast[forecast['ResourceName'] == resource_name]
    outturn_new = outturn[outturn['ResourceName'] == resource_name]

    labels = ['Average Outturn', 'Forecast Availability']
    counts = [outturn_new['Availability'].mean(), forecast_new['Availability'].mean()]
    bar_labels = ['Forecast', 'Outturn']
    bar_colors = ['tab:blue', 'tab:orange']
    
    plt.figure(figsize=(10, 10))
    plt.bar(labels, counts, label=bar_labels, color=bar_colors)
    plt.ylabel('Availability (MW)')
    plt.title(resource)
    plt.legend(title='Viotas Outturn vs Availability')
    plt.savefig(f"availability_against_resource_{resource}_bar.jpg")
    plt.close('all')

# Plotting Average Forecast vs Outturn Availability by Resource
names = resource_names.keys()
x_axis = np.arange(len(names))

forecast_means = forecast.groupby('ResourceName')['Availability'].mean()
outturn_means = outturn.groupby('ResourceName')['Availability'].mean()

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
plt.savefig("average_forecast_vs_outturn_availability_by_resource.jpg")
plt.close('all')

all_weekly_forecast_mwh = pd.DataFrame()
all_weekly_outturn_mwh = pd.DataFrame()

# Breakdown
for resource, resource_name in resource_names.items():
    forecast_new = forecast[forecast['ResourceName'] == resource_name].copy()
    outturn_new = outturn[outturn['ResourceName'] == resource_name].copy()

    # Halving the Availability do its MWh's
    forecast_new['MWh'] = forecast_new['Availability'] * 0.5
    outturn_new['MWh'] = outturn_new['Availability'] * 0.5

    # Using pandas string to date function so we can use the dates functionality
    forecast_new['Times'] = pd.to_datetime(forecast_new['Times'])
    outturn_new['Times'] = pd.to_datetime(outturn_new['Times'])

    # Changing the dataframes index to the time columns
    forecast_new.set_index('Times', inplace=True)
    outturn_new.set_index('Times', inplace=True)

    # Sampling the data weekly and setting it to start on the monday of each week
    weekly_forecast_mwh = forecast_new['MWh'].resample('W-MON').sum()
    weekly_outturn_mwh = outturn_new['MWh'].resample('W-MON').sum()

    all_weekly_forecast_mwh[resource] = weekly_forecast_mwh
    all_weekly_outturn_mwh[resource] = weekly_outturn_mwh

    plt.figure(figsize=(20, 12))
    plt.bar(weekly_forecast_mwh.index, weekly_forecast_mwh.values, label='Forecast MWh', width=2)
    plt.bar(weekly_outturn_mwh.index, weekly_outturn_mwh.values, label='Outturn MWh', width=2, align='edge')

    #only prints monday dates
    plt.xticks(weekly_forecast_mwh.index[weekly_forecast_mwh.index.dayofweek == 0],
            weekly_forecast_mwh.index[weekly_forecast_mwh.index.dayofweek == 0].strftime('%Y-%m-%d'),
            rotation=90)
    plt.xlabel('Week')
    plt.ylabel('MWh')
    plt.title(f'Weekly MWh for {resource}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"weekly_MWH_for_{resource}.jpg")
    plt.close('all')



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
plt.savefig("total_weekly_MWh_outturn_vs_availability")
plt.close('all')



for i in range(len(forecast_means)):
  difference_forecast_outturn = forecast_means[i] - outturn_means[i]
  print(difference_forecast_outturn)

for key in resource_names.keys():
  average_difference_for_resource={

  }
  print(key)




def summary_df(forecast,outturn):

  resource_summary = pd.DataFrame( columns = ['Name', 'Over Forecast', 'Under Forecast', 'Overall', 'Percentage Over', 'Percentage Under'])

  for Resource in resource_names:
    forecast_new = forecast[forecast['ResourceName']==resource_names[Resource]]
    outturn_new = outturn[outturn['ResourceName']==resource_names[Resource]]

    positive_diffs = []
    negative_diffs = []

    # Iterate through each row in OutturnNew
    for i in range(len(outturn_new)):

      forecast_availability = forecast_new['Availability'].iloc[i]
      outturn_availability = outturn_new['Availability'].iloc[i]
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

OverallSummary = summary_df(forecast,outturn)
forecast.to_csv ('forecast.csv', index = False, header=True)
outturn.to_csv ('outturn.csv', index = False, header=True)



def split_dataframe_weekly(df, time_column='Times'):
    # Ensure the time column is in datetime format
    df[time_column] = pd.to_datetime(df[time_column])

    # Set the time column as the index
    newdf = df.set_index(time_column, inplace=False)

    # Resample the DataFrame weekly, starting on Mondays
    weekly_dfs = {}
    for start_date, week_df in newdf.resample('W-MON'):
        weekly_dfs[start_date] = week_df

    return weekly_dfs

forecast_weekly = split_dataframe_weekly(forecast)
outturn_weekly = split_dataframe_weekly(outturn)

# Save each weekly dataframe to a separate CSV file
for start_date, weekly_df in forecast_weekly.items():
    weekly_df.to_csv(f'forecast_weekly_{start_date.date()}.csv', index=False, header=True)

for start_date, weekly_df in outturn_weekly.items():
    weekly_df.to_csv(f'outturn_weekly_{start_date.date()}.csv', index=False, header=True)

# Generating summary for each weekly split
for start_date in forecast_weekly.keys():
    summary = summary_df(forecast_weekly[start_date], outturn_weekly[start_date])
    summary.to_csv(f'summary_{start_date.date()}.csv', index=False, header=True)