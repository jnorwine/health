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


# use qs_ledger's script to parse the apple health xml to multiple csv files
# this only needs to be done if there is new data
# should put this in an if statement that checks if there is new data
# where does the output go???

parser_path = "D:\\Git\\qs_ledger\\apple_health\\apple-health-data-parser.py"
xml_path = "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\export.xml"

def parse_xml(parser_path: str, xml_path: str) -> None:
    subprocess.call(["python", parser_path, xml_path])

def read_mass_csv(path: str) -> pd.DataFrame:
    mass_df = pd.read_csv(path)
    mass_df = mass_df[mass_df["sourceName"] == "Health"]
    mass_df.drop(["type", "sourceName", "sourceVersion", "device", "startDate", "endDate"], axis=1, inplace=True)
    mass_df["event"] = "mass"
    mass_df.rename(columns={"creationDate":"datetime"}, inplace=True)
    mass_df.set_index("datetime", inplace=True)
    mass_df.index = pd.to_datetime(mass_df.index)
    return mass_df

def read_sleep_csv(path: str) -> pd.DataFrame:
    sleep_df = pd.read_csv(path)
    sleep_df.drop(["type", "sourceName", "sourceVersion", "device", "creationDate", "value"], axis=1, inplace=True)
    sleep_start_df = pd.DataFrame([pd.to_datetime(sleep_df.startDate)]).T
    sleep_start_df.columns=["datetime"]
    sleep_start_df["event"] = "sleep_start"
    sleep_end_df = pd.DataFrame([pd.to_datetime(sleep_df.endDate)]).T
    sleep_end_df.columns=["datetime"]
    sleep_end_df["event"] = "sleep_end"
    sleep_df = pd.concat([sleep_start_df, sleep_end_df])
    sleep_df.set_index("datetime", inplace=True)
    return sleep_df



class HealthFrame():
    """
    """

    def __init__(self, df):

        if type(df) == pd.core.frame.DataFrame:
            self.df = df
        elif type(df) == list:
            self.df = pd.concat(df)
        else:
            raise ValueError("you must pass either a dataframe or a list of dataframes")

        self.event_types = self.df["event"].unique()

    def add_event(self, df) -> None:
        """
        """

        if type(df) is not list:
            df = [df]

        df.append(self.df)
        self.df = pd.concat(df)

        self.event_types = self.df["event"].unique()

    def plot_event(self, events, ax=None) -> None:
        """
        """

        if type(events) == str:
            events = [events]

        if ax == None:
            fig, ax = plt.subplots()

        for event in events:
            group = self.df.groupby("event").get_group(event)
            ax.scatter(group.index, group.value)

    def time_to_next(self, event: str) -> pd.DataFrame:
        """return dataframe showing all entries of event with another column stating the time until its next occurence"""

        pass
        


# # plot mass vs datetime, color coded by time of day
# plt.figure(figsize=(10, 5))
#
# plt.plot(mass_start_datetime, mass_value)
# plt.scatter(mass_start_datetime, mass_value, c=[
#             dt.time().hour for dt in mass_start_datetime])
# plt.colorbar()
#
#
# workout_df = pd.read_csv(
#     "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\Workout.csv")
#
# # read sleep csv, and find start/end datetimes for every sleep session
# sleep_df = pd.read_csv(
#     "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\SleepAnalysis.csv")
# sleep_start_datetime = [datetime.strptime(
#     string, "%Y-%m-%d %H:%M:%S -0600") for string in sleep_df.startDate]
# sleep_end_datetime = [datetime.strptime(
#     string, "%Y-%m-%d %H:%M:%S -0600") for string in sleep_df.endDate]
#
#
# # read hrv csv, put values and start datetimes into their own variables
# hrv_df = pd.read_csv(
#     "D:\\Personal\\Programming\\Health\\export\\apple_health_export\\HeartRateVariabilitySDNN.csv")
# hrv_value = hrv_df.value
# hrv_start_datetime = [datetime.strptime(
#     string, "%Y-%m-%d %H:%M:%S -0600") for string in hrv_df.startDate]
#
#
# # plot all hrv values, and draw vertical lines every time sleep session ends
# plt.figure(figsize=(20, 5))
#
# plt.xlim(hrv_start_datetime[0], hrv_start_datetime[-1])
# plt.plot(hrv_start_datetime, hrv_value)
# plt.scatter(hrv_start_datetime, hrv_value, c=[
#             dt.time().hour for dt in hrv_start_datetime])
#
# for mark in sleep_end_datetime:
#     plt.axvline(x=mark, c="violet", alpha=0.5)
#
# # st.pyplot()
#
#
# # make a dataframe of sleep endtimes with the time until next sleep end
# sleep_end_df = pd.DataFrame()
# sleep_end_df["end_datetime"] = sleep_end_datetime
# sleep_end_df["time_to_next"] = [(sleep_end_datetime[i + 1] - sleep_end_datetime[i]).total_seconds()
#                                 for i in range(len(sleep_end_datetime) - 1)] + [None]
#
#
# # make a boolean column in sleep_end_df, true if some wake time has a local max time to next
# a = sleep_end_df.time_to_next.values
# sleep_end_df["local_max"] = np.r_[True, a[1:] >
#                                   a[:-1] + 10000] & np.r_[a[:-1] > a[1:] + 10000, True]
#
#
# # plot all hrv values, and draw vertical lines every time a sleep session ends with a long time until the next
# # the idea here is to draw vertical lines where I actually woke up in the morning for the day
# plt.figure(figsize=(20, 5))
#
# plt.xlim(hrv_start_datetime[0], hrv_start_datetime[-1])
# plt.plot(hrv_start_datetime, hrv_value)
# plt.scatter(hrv_start_datetime, hrv_value, c=[
#             dt.time().hour for dt in hrv_start_datetime])
#
# for mark in sleep_end_df[sleep_end_df["local_max"] == True].end_datetime.values:
#     plt.axvline(x=mark, c="violet", alpha=0.8)
#
# # st.pyplot()
#
#
# # add a new "event" column to sleep_end_df that equals "wake" for all wake up events (this whole df)
# # preparing to combine with hrv dff
# sleep_end_df["event"] = ["wake" for i in range(len(sleep_end_df))]
#
#
# # make a new df wake_df of the morning wakeups from sleep_end_df
# wake_df = sleep_end_df[sleep_end_df["local_max"] == True]
# wake_df.rename(columns={"end_datetime": "datetime"}, inplace=True)
#
#
# # make an abbreviated dataframe with just the essential information from hrv_df
# hrv_brief_df = pd.DataFrame()
# hrv_brief_df["datetime"] = hrv_start_datetime
# hrv_brief_df["event"] = "hrv"
# hrv_brief_df["value"] = hrv_value
#
#
# # combine wake and hrv events into one dataframe wake_hrv_df
# wake_hrv_df = pd.concat([wake_df, hrv_brief_df])
#
#
# # sort and reindex wake_hrv_df
# wake_hrv_df.sort_values("datetime", inplace=True)
# wake_hrv_df.reset_index(drop=True, inplace=True)
#
#
# # find hrv values immediately preceded by "wake event"
# # put their values and datetimes into two separate, new lists
# wake_hrv_value_list = []
# wake_hrv_datetime_list = []
#
# for wake_index in wake_hrv_df.index[wake_hrv_df["event"] == "wake"].tolist():
#
#     wake_hrv_value = wake_hrv_df.iloc[wake_index + 1].value
#     wake_hrv_datetime = wake_hrv_df.iloc[wake_index + 1].datetime
#
#     wake_hrv_value_list.append(wake_hrv_value)
#     wake_hrv_datetime_list.append(wake_hrv_datetime)
#
#
# # plot time series of morning wakeup hrv
# plt.figure(figsize=(15, 5))
# plt.plot(wake_hrv_datetime_list, wake_hrv_value_list)
# plt.scatter(wake_hrv_datetime_list, wake_hrv_value_list)
#
# # st.pyplot()
