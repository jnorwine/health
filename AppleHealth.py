
# run the script to put xml file into a bunch of csv files
# %run -i ‘apple-health-data-parser’ ‘export.xml’

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from collections import OrderedDict
import subprocess
import os
import streamlit as st

# WHAT DOES THIS COMMAND DO?
# this only needs to be done if there is new data
#subprocess.call(["python", "D:\\Git\\qs_ledger\\apple_health\\apple-health-data-parser.py", "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\export.xml"])


# list of csv files from apple health
#next(os.walk("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\"))[2]


mass_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\BodyMass.csv")

# save some columns from mass_df into their own variables
mass_start_datetime_string = mass_df[mass_df.sourceName == "Health"].startDate
mass_start_datetime = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S -0600") for string in mass_start_datetime_string]
mass_value = mass_df[mass_df.sourceName == "Health"].value

# plot mass vs datetime, color coded by time of day
plt.figure(figsize=(10,5))

plt.plot(mass_start_datetime, mass_value)
plt.scatter(mass_start_datetime, mass_value, c=[dt.time().hour for dt in mass_start_datetime])
plt.colorbar()

#st.pyplot()



workout_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\Workout.csv")

# read sleep csv, and find start/end datetimes for every sleep session
sleep_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\SleepAnalysis.csv")
sleep_start_datetime_string = sleep_df.startDate
sleep_end_datetime_string = sleep_df.endDate
sleep_start_datetime = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S -0600") for string in sleep_start_datetime_string]
sleep_end_datetime = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S -0600") for string in sleep_end_datetime_string]



# read hrv csv, put values and start datetimes into their own variables
hrv_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\HeartRateVariabilitySDNN.csv")
hrv_start_datetime_string = hrv_df.startDate
hrv_value = hrv_df.value
hrv_start_datetime = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S -0600") for string in hrv_start_datetime_string]


# plot all hrv values, and draw vertical lines every time sleep session ends
plt.figure(figsize=(20,5))

plt.xlim(hrv_start_datetime[0], hrv_start_datetime[-1])
plt.plot(hrv_start_datetime, hrv_value)
plt.scatter(hrv_start_datetime, hrv_value, c=[dt.time().hour for dt in hrv_start_datetime])

for mark in sleep_end_datetime:
    plt.axvline(x=mark, c="violet", alpha=0.5)

#st.pyplot()



# make a dataframe of sleep endtimes with the time until next sleep end
sleep_end_df = pd.DataFrame()
sleep_end_df["end_datetime"] = sleep_end_datetime
sleep_end_df["time_to_next"] = [(sleep_end_datetime[i+1] - sleep_end_datetime[i]).total_seconds() for i in range(len(sleep_end_datetime)-1)] + [None]


# make a boolean column in sleep_end_df, true if some wake time has a local max time to next
a = sleep_end_df.time_to_next.values
sleep_end_df["local_max"] = np.r_[True, a[1:] > a[:-1] + 10000] & np.r_[a[:-1] > a[1:] + 10000, True]



# plot all hrv values, and draw vertical lines every time a sleep session ends with a long time until the next
# the idea here is to draw vertical lines where I actually woke up in the morning for the day
plt.figure(figsize=(20,5))

plt.xlim(hrv_start_datetime[0], hrv_start_datetime[-1])
plt.plot(hrv_start_datetime, hrv_value)
plt.scatter(hrv_start_datetime, hrv_value, c=[dt.time().hour for dt in hrv_start_datetime])

for mark in sleep_end_df[sleep_end_df["local_max"] == True].end_datetime.values:
    plt.axvline(x=mark, c="violet", alpha=0.8)

#st.pyplot()


# add a new "event" column to sleep_end_df that equals "wake" for all wake up events (this whole df)
# preparing to combine with hrv dff
sleep_end_df["event"] = ["wake" for i in range(len(sleep_end_df))]



# make a new df wake_df of the morning wakeups from sleep_end_df
wake_df = sleep_end_df[sleep_end_df["local_max"] == True]
wake_df.rename(columns={"end_datetime" : "datetime"}, inplace=True)



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
plt.figure(figsize=(15,5))
plt.plot(wake_hrv_datetime_list, wake_hrv_value_list)
plt.scatter(wake_hrv_datetime_list, wake_hrv_value_list)

#st.pyplot()


# read strongapp export csv into strong_df
strong_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\strong.csv")


# put data from "Date" column into new column "datetime" in datetime format
strong_df["datetime"] = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S") for string in strong_df["Date"]]
strong_df["lbs*reps"] = strong_df["Weight"] * strong_df["Reps"]


#
#st.write(strong_df[(strong_df["Exercise Name"] == "AnCap Repeaters (Assisted)") | (strong_df["Exercise Name"] == "AnCap Repeaters")])


#
strong_wake_hrv_df = pd.concat([strong_df, wake_hrv_df])
strong_wake_hrv_df.sort_values("datetime", inplace=True)
strong_wake_hrv_df.reset_index(drop=True, inplace=True)


#st.write(strong_wake_hrv_df)

ancap_datetimes = np.unique(strong_df[(strong_df["Exercise Name"] == "AnCap Repeaters (Assisted)") | (strong_df["Exercise Name"] == "AnCap Repeaters")].datetime.values)

#unix timestamp from datetime64
ancap_timestamp_min = (ancap_datetimes.min() - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
ancap_timestamp_max = (ancap_datetimes.max() - np.datetime64("1970-01-01T00:00:00Z")) / np.timedelta64(1, "s")

# default values
xmin = ancap_timestamp_min
xmax = ancap_timestamp_max

#xmin = st.slider("xmin", ancap_timestamp_min-1, ancap_timestamp_max+1, ancap_timestamp_min)
#xmax = st.slider("xmax", ancap_timestamp_min-1, ancap_timestamp_max+1, ancap_timestamp_max)
#

#st.subtitle("HRV vs ancap workouts")
plt.figure(figsize=(10,5))

for mark in ancap_datetimes:
    plt.axvline(x=mark, c="gold", alpha=0.8, label="ancap")
plt.plot(wake_hrv_datetime_list, wake_hrv_value_list)

plt.xlim((datetime.utcfromtimestamp(xmin), datetime.utcfromtimestamp(xmax)))

#st.pyplot()

################## BELOW CODE HAS NOT BEEN ORGANIZED ############

st.header("Workouts from Strong")

strong_df["treat_weight"] = ""
strong_df.loc[strong_df["Exercise Name"] == "AnCap Repeaters (Assisted)", "treat_weight"] = "sub_from_bw"
strong_df["true_weight"] = ""
strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "true_weight"] = strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "bw"] - strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "weight"]

st.write(strong_df)

st.subheader("Specific Exercise")
exercise = st.text_input("Exercise")
st.write(strong_df[strong_df["Exercise Name"] == exercise])

st.subheader("Performance over time, grouped by day")
metric = "lbs*reps"
metric = st.text_input("Metric")
values = strong_df[strong_df["Exercise Name"] == exercise][metric]
times = strong_df[strong_df["Exercise Name"] == exercise]["datetime"]

spec_perf_df = pd.concat([values, times], axis=1).reset_index().drop("index", axis="columns")
st.write(spec_perf_df)

unique_times = times.unique()
for unique_time in unique_times:
    st.write(spec_perf_df[spec_perf_df["datetime"] == unique_time]["lbs*reps"].sum())





















# # plot a vertical line every time I work out, color coded by workout name
#
# plt.figure(figsize=(15,5))
#
# plt.xlim((737293.8399186282, 737324.695081372))
# plt.plot(wake_hrv_datetime_list, wake_hrv_value_list)
# plt.scatter(wake_hrv_datetime_list, wake_hrv_value_list)
#
# for name in strong_df["Workout Name"].unique():
#     name_df = strong_df[strong_df["Workout Name"] == name]
#     color = np.random.rand(3,)
#     for datetime in name_df["datetime"]:
#         plt.axvline(x=datetime, c=color, label=name)
#
#
# handles, labels = plt.gca().get_legend_handles_labels()
# by_label = OrderedDict(zip(labels, handles))
# plt.legend(by_label.values(), by_label.keys())
#
#
# # In[ ]:
#
#
# # color code blocks of time for training blocks
#
# # loop until user says no
# date_input_string = input("datetime YYYY-MM-DD") + "00:00:00"
# block_start_datetime = datetime.strptime(date_input_string, "%Y-%m-%d %H:%M:%S")
# block_type = input("block type")
# block_stop_datetime_string = input("ending datetime YYYY-MM-DD")
# block_stop_datetime = datetime.strptime(block_stop_datetime_string, "%Y-%m-%d %H:%M:%S")
# # print(again? Y/N)
#
#
# # for datetime in start list, append datetime to datetime list
# # append "start" to event list
# # append block type to block type list
#
# #for datetime in stop list, append datetime to datetimelist
# # append "stop" to event list
# # append block type to block type list
#
# # build block_df from lists above
#
# # concat block df and hrv_wake_df
#
# # plot axhspan from block start to block stop, color coded by block type
# # add this plot to hrv/workout plot
#
#
# # In[ ]:
