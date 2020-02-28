"""
Handle import, cleaning and manipulation of data from Strongapp.
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class StrongFrame():
    """
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df.Date = pd.to_datetime(self.df.Date)
        self.df.set_index(["Date", "Workout Name", "Exercise Name", "Set Order"], inplace=True)

        self.workouts = self.df.groupby("Workout Name")
        self.exercises = self.df.groupby("Exercise Name")
        self.sessions = self.df.groupby("Date")

        self.workout_list = list(self.workouts.groups.keys())
        self.exercise_list = list(self.exercises.groups.keys())
        self.session_list = list(self.sessions.groups.keys())

        self.exercise_metadata = {exercise:{} for exercise in self.exercise_list}

        self.metrics = self.df.columns

    def __repr__(self):
        print(self.df)
        return f"{self.df.shape[0]} rows x {self.df.shape[1]} columns"


    def set_relevance(self, exercise: str, stats: list) -> None:
        """
        """

        if exercise == "all":
            for key in self.exercise_metadata.keys():
                self.exercise_metadata[key]["relevance"] = stats
        else:
            self.exercise_metadata[exercise]["relevance"] = stats


    def get_times(self, event) -> list:
        """
        """

        if event in self.exercise_list:
            return [self.exercises.groups[event].levels[0][label] for label in self.exercises.groups[event].labels[0]]
        elif event in self.workout_list:
            return [self.workouts.groups[event].levels[0][label] for label in self.workouts.groups[event].labels[0]]
        else:
            raise ValueError(f"could not find \"{event}\" in list of workouts or exercises")


    def plot_event(self, event: str, metric=None, ax=None) -> None:
        """
        """

        times = self.get_times(event)
        if event in self.exercise_list:
            group = self.exercises.get_group(event)
            event_type = "exercise"
            if metric not in self.metrics:
                raise ValueError(f"could not find \"{metric}\" in list of metrics")

        elif event in self.workout_list:
            group = self.workouts.get_group(event)
            event_type = "workout"
        else: raise ValueError(f"could not find \"{event}\" in exercise or workout list")

        if ax is None:
            fig, ax = plt.subplots()
            ax.set_xlim((min(times)-timedelta(5), max(times)+timedelta(5)))

        if event_type == "exercise":
            ax.scatter(times, group[metric], label=f"{event}:{metric}")
        elif event_type == "workout":
            for time in times: ax.axvline(time)

    def plot(self, ax=None):
        """
        """

        if ax is None:
            fig, ax = plt.subplots()

        return self.df.plot(ax=ax)


    def add_metric(metric: str) -> None:
        """parse user-inputted string for mathematical combination of existing metrics"""

        pass


def read_strong_csv(path: str) -> StrongFrame:
    """
    """

    df = pd.read_csv(path)
    return StrongFrame(df)




# strong_wake_hrv_df = pd.concat([strong_df, wake_hrv_df])
# strong_wake_hrv_df.sort_values("datetime", inplace=True)
# strong_wake_hrv_df.reset_index(drop=True, inplace=True)
#
#
# #xmin = st.slider("xmin", ancap_timestamp_min-1, ancap_timestamp_max+1, ancap_timestamp_min)
# #xmax = st.slider("xmax", ancap_timestamp_min-1, ancap_timestamp_max+1, ancap_timestamp_max)
# #
#
# #st.subtitle("HRV vs ancap workouts")
# plt.figure(figsize=(10, 5))
#
# for mark in ancap_datetimes:
#     plt.axvline(x=mark, c="gold", alpha=0.8, label="ancap")
# plt.plot(wake_hrv_datetime_list, wake_hrv_value_list)
#
# plt.xlim((datetime.utcfromtimestamp(xmin), datetime.utcfromtimestamp(xmax)))
#
# # st.pyplot()
#
# ################## BELOW CODE HAS NOT BEEN ORGANIZED ############
#
# st.header("Workouts from Strong")
#
# strong_df["treat_weight"] = ""
# strong_df.loc[strong_df["Exercise Name"] ==
#               "AnCap Repeaters (Assisted)", "treat_weight"] = "sub_from_bw"
# strong_df["true_weight"] = ""
# strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "true_weight"] = strong_df.loc[strong_df["treat_weight"]
#                                                                                          == "sub_from_bw", "bw"] - strong_df.loc[strong_df["treat_weight"] == "sub_from_bw", "weight"]
#
# st.write(strong_df)
#
# st.subheader("Specific Exercise")
# exercise = st.text_input("Exercise")
# st.write(strong_df[strong_df["Exercise Name"] == exercise])
#
# st.subheader("Performance over time, grouped by day")
# metric = "lbs*reps"
# metric = st.text_input("Metric")
# values = strong_df[strong_df["Exercise Name"] == exercise][metric]
# times = strong_df[strong_df["Exercise Name"] == exercise]["datetime"]
#
# spec_perf_df = pd.concat([values, times], axis=1).reset_index().drop(
#     "index", axis="columns")
# st.write(spec_perf_df)
#
# unique_times = times.unique()
# for unique_time in unique_times:
#     st.write(spec_perf_df[spec_perf_df["datetime"]
#                           == unique_time]["lbs*reps"].sum())
