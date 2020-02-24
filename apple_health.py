"""
Handle import, cleaning, and manipulation of data from Apple Health.
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from collections import OrderedDict
import subprocess
import os


# run the script to put xml file into a bunch of csv files
# %run -i ‘apple-health-data-parser’ ‘export.xml’


# use someone else's script to parse the apple health xml to multiple csv files
# this only needs to be done if there is new data
# should put this in an if statement that checks if there is new data
#subprocess.call(["python", "D:\\Git\\qs_ledger\\apple_health\\apple-health-data-parser.py", "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\export.xml"])


# list of csv files from apple health
# next(os.walk("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\"))[2]


mass_df = pd.read_csv(
    "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\BodyMass.csv")

# save some columns from mass_df into their own variables
mass_start_datetime_string = mass_df[mass_df.sourceName == "Health"].startDate
mass_start_datetime = [datetime.strptime(
    string, "%Y-%m-%d %H:%M:%S -0600") for string in mass_start_datetime_string]
mass_value = mass_df[mass_df.sourceName == "Health"].value

# plot mass vs datetime, color coded by time of day
plt.figure(figsize=(10, 5))

plt.plot(mass_start_datetime, mass_value)
plt.scatter(mass_start_datetime, mass_value, c=[
            dt.time().hour for dt in mass_start_datetime])
plt.colorbar()


workout_df = pd.read_csv(
    "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\Workout.csv")

# read sleep csv, and find start/end datetimes for every sleep session
sleep_df = pd.read_csv(
    "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\SleepAnalysis.csv")
sleep_start_datetime = [datetime.strptime(
    string, "%Y-%m-%d %H:%M:%S -0600") for string in sleep_df.startDate]
sleep_end_datetime = [datetime.strptime(
    string, "%Y-%m-%d %H:%M:%S -0600") for string in sleep_df.endDate]


# read hrv csv, put values and start datetimes into their own variables
hrv_df = pd.read_csv(
    "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\HeartRateVariabilitySDNN.csv")
hrv_value = hrv_df.value
hrv_start_datetime = [datetime.strptime(
    string, "%Y-%m-%d %H:%M:%S -0600") for string in hrv_df.startDate]


# plot all hrv values, and draw vertical lines every time sleep session ends
plt.figure(figsize=(20, 5))

plt.xlim(hrv_start_datetime[0], hrv_start_datetime[-1])
plt.plot(hrv_start_datetime, hrv_value)
plt.scatter(hrv_start_datetime, hrv_value, c=[
            dt.time().hour for dt in hrv_start_datetime])

for mark in sleep_end_datetime:
    plt.axvline(x=mark, c="violet", alpha=0.5)

# st.pyplot()


# make a dataframe of sleep endtimes with the time until next sleep end
sleep_end_df = pd.DataFrame()
sleep_end_df["end_datetime"] = sleep_end_datetime
sleep_end_df["time_to_next"] = [(sleep_end_datetime[i + 1] - sleep_end_datetime[i]).total_seconds()
                                for i in range(len(sleep_end_datetime) - 1)] + [None]


# make a boolean column in sleep_end_df, true if some wake time has a local max time to next
a = sleep_end_df.time_to_next.values
sleep_end_df["local_max"] = np.r_[True, a[1:] >
                                  a[:-1] + 10000] & np.r_[a[:-1] > a[1:] + 10000, True]


# plot all hrv values, and draw vertical lines every time a sleep session ends with a long time until the next
# the idea here is to draw vertical lines where I actually woke up in the morning for the day
plt.figure(figsize=(20, 5))

plt.xlim(hrv_start_datetime[0], hrv_start_datetime[-1])
plt.plot(hrv_start_datetime, hrv_value)
plt.scatter(hrv_start_datetime, hrv_value, c=[
            dt.time().hour for dt in hrv_start_datetime])

for mark in sleep_end_df[sleep_end_df["local_max"] == True].end_datetime.values:
    plt.axvline(x=mark, c="violet", alpha=0.8)

# st.pyplot()


# add a new "event" column to sleep_end_df that equals "wake" for all wake up events (this whole df)
# preparing to combine with hrv dff
sleep_end_df["event"] = ["wake" for i in range(len(sleep_end_df))]


# make a new df wake_df of the morning wakeups from sleep_end_df
wake_df = sleep_end_df[sleep_end_df["local_max"] == True]
wake_df.rename(columns={"end_datetime": "datetime"}, inplace=True)


# make an abbreviated dataframe with just the essential information from hrv_df
hrv_brief_df = pd.DataFrame()
hrv_brief_df["datetime"] = hrv_start_datetime
hrv_brief_df["event"] = "hrv"
hrv_brief_df["value"] = hrv_value


# combine wake and hrv events into one dataframe wake_hrv_df
wake_hrv_df = pd.concat([wake_df, hrv_brief_df])


# sort and reindex wake_hrv_df
wake_hrv_df.sort_values("datetime", inplace=True)
wake_hrv_df.reset_index(drop=True, inplace=True)


# find hrv values immediately preceded by "wake event"
# put their values and datetimes into two separate, new lists
wake_hrv_value_list = []
wake_hrv_datetime_list = []

for wake_index in wake_hrv_df.index[wake_hrv_df["event"] == "wake"].tolist():

    wake_hrv_value = wake_hrv_df.iloc[wake_index + 1].value
    wake_hrv_datetime = wake_hrv_df.iloc[wake_index + 1].datetime

    wake_hrv_value_list.append(wake_hrv_value)
    wake_hrv_datetime_list.append(wake_hrv_datetime)


# plot time series of morning wakeup hrv
plt.figure(figsize=(15, 5))
plt.plot(wake_hrv_datetime_list, wake_hrv_value_list)
plt.scatter(wake_hrv_datetime_list, wake_hrv_value_list)

# st.pyplot()
