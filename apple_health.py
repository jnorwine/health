"""
Handle import, cleaning, and manipulation of data from Apple Health.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as collections
from datetime import datetime
import subprocess


# use qs_ledger's script to parse the apple health xml to multiple csv files
# this only needs to be done if there is new data
# should put this in an if statement that checks if there is new data
# where does the output go???
def parse_xml(parser_path: str, xml_path: str) -> None:
    """
    """

    subprocess.call(["python", parser_path, xml_path])

def read_mass_csv(path: str) -> pd.DataFrame:
    """
    """

    mass_df = pd.read_csv(path)
    mass_df = mass_df[mass_df["sourceName"] == "Health"]
    mass_df.drop(["type", "sourceName", "sourceVersion", "device", "startDate", "endDate"], axis=1, inplace=True)
    mass_df["event"] = "mass"
    mass_df.rename(columns={"creationDate":"datetime"}, inplace=True)
    mass_df.set_index("datetime", inplace=True)
    mass_df.index = pd.to_datetime(mass_df.index)
    return mass_df

def read_sleep_csv(path: str) -> pd.DataFrame:
    """
    """

    sleep_df = pd.read_csv(path)
    sleep_df.drop(["type", "sourceName", "sourceVersion", "device", "creationDate", "value"], axis=1, inplace=True)
    sleep_start_df = pd.DataFrame(sleep_df.startDate)
    sleep_start_df.columns=["datetime"]
    sleep_start_df["event"] = "sleep_start"
    sleep_end_df = pd.DataFrame(sleep_df.endDate)
    sleep_end_df.columns=["datetime"]
    sleep_end_df["event"] = "sleep_end"
    sleep_df = pd.concat([sleep_start_df, sleep_end_df])
    sleep_df.set_index("datetime", inplace=True)
    sleep_df.index = pd.to_datetime(sleep_df.index)
    return sleep_df


def read_hrv_csv(path: str) -> pd.DataFrame:
    """
    """

    hrv_df = pd.read_csv(path)
    hrv_df.drop(["sourceName", "sourceVersion", "device", "type", "startDate", "endDate"], axis=1, inplace=True)
    hrv_df["event"] = "hrv"
    hrv_df.rename(columns={"creationDate":"datetime"}, inplace=True)
    hrv_df.set_index("datetime", inplace=True)
    hrv_df.index = pd.to_datetime(hrv_df.index)
    return hrv_df


def is_maxima(list_like, n=5):
    """
    find values in list_like that are greater than the surrounding n values on either side

    return: boolean array
    """
    pass


def is_minimum(list_like, n=5):
    """
    find values in list_like that are less than the surrounding n values on either side

    return: boolean array
    """
    pass



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

    def __repr__(self):
        return self.df.__repr__()


    def add_event(self, df: pd.DataFrame) -> HealthFrame:
        """
        """

        if type(df) is not list:
            df = [df]

        df.append(self.df)
        self.df = pd.concat(df, sort=True)

        self.event_types = self.df["event"].unique()
        self.df.sort_index(inplace=True)

        return self

    def scatter_event(self, events, ax=None, alpha=None) -> collections.PathCollection:
        """
        """

        if type(events) == str:
            events = [events]

        if ax is None:
            fig, ax = plt.subplots()


        for event in events:
            group = self.df.groupby("event").get_group(event)
            scatter = ax.scatter(group.index, group.value, alpha=alpha)

        return scatter

    def vline_event(self, events, ax=None, alpha=None, where=None) -> collections.PathCollection:
        """
        """

        if type(events) == str:
            events = [events]

        if ax is None:
            fig, ax = plt.subplots()

        if where is None:
            where = np.full(self.df.shape[0], True)

        for event in events:
            print(type(where))
            group = self.df.groupby("event").get_group(event)[where]
            vlines = [ax.axvline(x=_x, alpha=alpha) for _x in group.index]

        return vlines

    def plot(self, ax=None):
        """
        """

        if ax is None:
            fig, ax = plt.subplots()

        return self.df.plot(ax=ax)


    def time_to_next(self, event: str) -> pd.Series:
        """return series showing all entries of event with another column
        stating the time until its next occurence"""

        event_df = self.df[self.df["event"] == event]
        time_to_next = [event_df.index.tolist()[i+1] - event_df.index.tolist()[i] for i, _  in enumerate(event_df["event"][:-1])]
        time_to_next.append(np.nan)
        time_to_next_series = pd.Series(time_to_next)

        return time_to_next_series

    def time_to_prev(self, event: str) -> np.ndarray:
        """
        """

        event_df = self.df[self.df["event"] == event]
        time_to_prev = [event_df.index.tolist()[i] - event_df.index.tolist()[i-1] for i, _  in enumerate(event_df["event"][1:])]
        time_to_prev.insert(0, np.nan)
        time_to_prev_array = np.array(time_to_prev)

        return time_to_prev_array

    def preceded_by(self, events) -> np.ndarray:
        """
        """

        if type(events) == str:
            events = [events]

        list = [self.df["event"][i-1] in events for i, _ in enumerate(self.df["event"][1:])]
        list.insert(0, False)
        return np.array(list)

    def get_event(self, events) -> np.ndarray:
        """
        """

        if type(events) == str:
            events = [events]

        return HealthFrame(self.df[[event in events for event in self.df["event"]]])

    def where(self, where) -> HealthFrame:
        """
        """

        return HealthFrame(self.df[where])




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
#



# # make a boolean column in sleep_end_df, true if some wake time has a local max time to next
# a = sleep_end_df.time_to_next.values
# sleep_end_df["local_max"] = np.r_[True, a[1:] >
#                                   a[:-1] + 10000] & np.r_[a[:-1] > a[1:] + 10000, True]
#
##
#
