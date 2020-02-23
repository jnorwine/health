
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

#subprocess.call(["python", "D:\\Git\\qs_ledger\\apple_health\\apple-health-data-parser.py", "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\export.xml"])
# this only needs to be done if there is new data

# list of csv files from apple health
#next(os.walk("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\"))[2]

strong_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\strong.csv")
mass_df = pd.read_csv("D:\\Personal\\Programming\\Health\\export\\apple_health_export\\BodyMass.csv")

# save some columns from mass_df into their own variables
mass_df = mass_df[mass_df.sourceName == "Health"]
mass_start_datetime_string = mass_df.startDate
mass_start_datetime = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S -0600") for string in mass_start_datetime_string]
mass_value = mass_df[mass_df.sourceName == "Health"].value
mass_df["datetime"] = mass_start_datetime
st.write(mass_df)

st.subheader("strong_df")
strong_df["datetime"] = [datetime.strptime(string, "%Y-%m-%d %H:%M:%S") for string in strong_df["Date"]]
strong_df["lbs*reps"] = strong_df["Weight"] * strong_df["Reps"]
strong_df["bw"] = np.nan
st.write(strong_df)

################################################################ THE WALL ############

#st.header("Workouts from Strong")

# add most recent bodyweight to every line in strong_df

# return the most recent datetime in pandas timeseries relative to date
def most_recent(timeseries, input_dt):
    most_recent_dt = np.nan # for input_dt earlier than all dt
    for dt in timeseries:
        #st.write(dt)
        if input_dt > dt:
            #st.write("input time is after than this date")
            #st.write("input: " + str(input_dt) + "<" + str(dt))
            most_recent_dt = dt
        else:
            #st.write("input time is on or before this date")
            #most_recent_dt = dt
            pass

    return most_recent_dt



# generalize this, eg def fill_with_most_recent(from_df, into_df)
for index, row in strong_df.iterrows():
    bw_datetime = most_recent(mass_df["datetime"], row["datetime"])
    try:
        mass_value = mass_df[mass_df["datetime"] == bw_datetime]["value"][0]
    except:
        mass_value = np.nan

    # st.write("the value I want to put in:")
    # st.write(mass_value)
    # st.write(type(mass_value))

    # st.write("index")
    # st.write(index)
    # st.write("column location")
    # st.write(strong_df.columns.get_loc("bw"))

    # slot = strong_df.iloc[index, strong_df.columns.get_loc("bw")]
    # st.write("the value that is currently there:")
    # st.write(slot)

    strong_df.iloc[index, strong_df.columns.get_loc("bw")] = mass_value

    # st.write("the value in there now:")
    # st.write(strong_df.iloc[index, strong_df.columns.get_loc("bw")])

    # st.write("###############################################")


# calculate true weights based on value for "treat_weight"

# strong_df["treat_weight"] = ""
# strong_df.loc[strong_df["Exercise Name"] == "AnCap Repeaters (Assisted)", "treat_weight"] = "sub_from_bw"
# strong_df["true_weight"] = ""
# strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "true_weight"] = strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "bw"] - strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "weight"]






# st.write(strong_df)
#
# st.subheader("Specific Exercise")
# exercise = st.text_input("Exercise")
# st.write(strong_df[strong_df["Exercise Name"] == exercise])
#
# st.subheader("Performance over time, grouped by day")
# metric = st.text_input("Metric")
# if metric == "":
#     metric = "lbs*reps"
# values = strong_df[strong_df["Exercise Name"] == exercise][metric]
# times = strong_df[strong_df["Exercise Name"] == exercise]["datetime"]
#
# spec_perf_df = pd.concat([values, times], axis=1).reset_index().drop("index", axis="columns")
# st.write(spec_perf_df)
#
# unique_times = times.unique()
# for unique_time in unique_times:
#     st.write(spec_perf_df[spec_perf_df["datetime"] == unique_time]["lbs*reps"].sum())





















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
