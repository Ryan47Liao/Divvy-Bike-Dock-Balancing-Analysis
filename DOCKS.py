"""_summary_
DOCKs class is used to transform travel history data into Station dock capacity data (a time series)
by simulating changes in capacity given frequency.

Author: Ryan47Liao
Date: 2022-03-20
"""
#Packages
from impala.dbapi import connect
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta
# Graph
import networkx as nx
# Analysis 
from sklearn.cluster import KMeans, DBSCAN


class DOCKs:
    def __init__(self, date, trip_subset, df_Station_final, init_with_0=True):
        """_summary_
        DOCKs class is used to transform travel history data into Station dock capacity data (a time series)
        by simulating changes in capacity given frequency.
        
        Args:
            date (str): the date of interest 
            trip_subset (pd.DataFrame): a subset of travel history,usually all within a day
            df_Station_final (pd.DataFrame): a Dataset that contains station corrdinates 
            init_with_0 (bool, optional): Weather to initialize station docks by 0. Defaults to True. 
            (Then the intepretation changes from dock count to dock delta)
        """
        self.df_Station_final = df_Station_final.copy()
        self.Capacity = self.Get_Capacity()
        self.df = self.Data_Transform(trip_subset, date)
        self.Generate_Docks(df_Station_final, init_with_0)
        self.cursor = 0
        self.time_book = {0: self.df.loc[self.cursor].timestamp}
        self.df_Station_cluster_capacity = None

    def __repr__(self):
        return f"DOCK|{self.DF_Dock.shape }"

    def Data_Transform(self, trip_subset, date):
        """_summary_
        Transforms data by:
        1.Change DateString into Datetime Objects
        2.Merge with station to get docks info
        3.Create subsets of leaving and coming and Stack subsets together
        
        Args:
            trip_subset (pd.DataFrame): a subset of travel history,usually all within a day
            date (str): the date of interest 

        Returns:
            pd.DataFrame: _description_
        """
        trip_subset = trip_subset.copy()
        trip_subset["start_station_id"] = [
            str(id) for id in list(trip_subset["start_station_id"])
        ]
        trip_subset["end_station_id"] = [
            str(id) for id in list(trip_subset["end_station_id"])
        ]
        ########################
        # Change format for comparison
        trip_subset["started_at"] = trip_subset.started_at.apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        )
        trip_subset["ended_at"] = trip_subset.ended_at.apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        )
        ##################
        # Merge with station to get docks info
        trip_subset = trip_subset.merge(
            self.df_Station_final[["station_id", "Nbh_id", "com_id"]],
            left_on="start_station_id",
            right_on="station_id",
        )
        trip_subset = trip_subset.rename(
            columns={"Nbh_id": "start_Nbh_id", "com_id": "start_com_id"}
        ).drop(columns=["station_id"], axis=1)
        trip_subset = trip_subset.merge(
            self.df_Station_final[["station_id", "Nbh_id", "com_id"]],
            left_on="end_station_id",
            right_on="station_id",
        )
        trip_subset = trip_subset.rename(
            columns={"Nbh_id": "end_Nbh_id", "com_id": "end_com_id"}
        ).drop(columns=["station_id"], axis=1)
        ################################################################
        # Create subsets
        trip_subset_starts = trip_subset[
            ["started_at", "start_station_id", "start_Nbh_id", "start_com_id"]
        ]
        trip_subset_starts.insert(4, "Leaving", 1)
        trip_subset_starts = trip_subset_starts.rename(
            columns={
                "started_at": "timestamp",
                "start_station_id": "station_id",
                "start_Nbh_id": "Nbh_id",
                "start_com_id": "com_id",
            }
        )
        trip_subset_ends = trip_subset[
            ["ended_at", "end_station_id", "end_Nbh_id", "end_com_id"]
        ]
        trip_subset_ends.insert(4, "Leaving", 0)
        trip_subset_ends = trip_subset_ends.rename(
            columns={
                "ended_at": "timestamp",
                "end_station_id": "station_id",
                "end_Nbh_id": "Nbh_id",
                "end_com_id": "com_id",
            }
        )
        ###############
        # Stack subsets together
        trip_subset_all = (
            pd.concat([trip_subset_starts, trip_subset_ends])
            .sort_values("timestamp")
            .reset_index(drop=True)
        )
        tmr_date = str(datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).split(" ")[0]
        return trip_subset_all.query(f'timestamp < "{tmr_date}"')

    def Generate_Docks(self, df_Station_final, init_with_0):
        """_summary_
        Initilize docks with default capacity 
        Args:
            df_Station_final (pd.DataFrame): a Dataset that contains station corrdinates 
            init_with_0 (bool, optional): Weather to initialize station docks by 0. Defaults to True. 
            (Then the intepretation changes from dock count to dock delta)
        """
        docks = sorted(df_Station_final.Nbh_id.unique())
        self.DF_Dock = pd.DataFrame(columns=docks)
        if init_with_0:
            self.DF_Dock = self.DF_Dock.append({d: 0 for d in docks}, ignore_index=True)
        else:  # init with total docks
            self.DF_Dock = self.DF_Dock.append(self.Capacity, ignore_index=True)
        self.DF_Dock = self.DF_Dock.reset_index(drop=True)

    def Get_Capacity(self):
        """_summary_
        Returns:
            dict: dock capacity by Neighbourhood
        """
        return dict(
            self.df_Station_final.groupby("Nbh_id")["Docks in Service"]
            .sum()
            .sort_index()
        )

    def _docks_update(self, time_start=None, time_mins=1):
        """_summary_
        Update all station's dock capacity by simulating over the travel history starting 'time_start' untill time_mins
        
        Args:
            time_start (_type_, optional): When does the simulation start. Defaults to None.
            time_mins (int, optional): How long does the simulation take place till stopping. Defaults to 1.
        """
        if time_start is None:
            time_start = self.df.loc[self.cursor].timestamp
        current_docks = {
            k: list(v.values())[0] for k, v in self.DF_Dock.tail(1).to_dict().items()
        }
        time_end = time_start + timedelta(minutes=time_mins)
        while self.df.loc[self.cursor].timestamp < time_end:
            next_trip = self.df.loc[self.cursor]
            # print(next_trip)
            if next_trip.Leaving == 1:
                current_docks[next_trip.Nbh_id] += 1
            else:
                current_docks[next_trip.Nbh_id] -= 1
            self.cursor += 1
        # After all updates
        self.DF_Dock = self.DF_Dock.append(current_docks, ignore_index=True)
        self.time_book[self.DF_Dock.shape[0] - 1] = time_end

    def Dock_Update(self, time_mins=10):
        """_summary_
        Keep simulating and update Dock capacity untill there is no data
        Args:
            time_mins (int, optional): _description_. Defaults to 10.
        """
        while True:
            try:
                self._docks_update(time_mins=time_mins)
            except KeyError:
                break

    def Get_Normalized_dock(self, normalize=True):
        """_summary_
        Args:
            normalize (bool, optional): Weather to normalize the data or not. Defaults to True.

        Returns:
            pd.DataFrame: Station Dock capacity table that's normalized by dock total capacity 
        """
        if normalize:
            out = self.DF_Dock / self.Capacity
        else:
            out = self.DF_Dock.copy()
        out["Time_Stamp"] = self.time_book.values()
        return out.set_index("Time_Stamp", drop=True)

    ########################################################################
    # Visualiation
    def Capacity_Analysis(self):
        """_summary_
        Enginer the following features:
        1. daily_capacity_low
        2. daily_capacity_high
        3. daily_capacity_mean
        4. daily_capacity_median
        Into the df_Station_final DataFrame. 
        Returns:
            pd.DataFrame: A new Station Table with descriptive features 
        """
        Dock_Normal = self.Get_Normalized_dock()
        ################
        df_Capacity = pd.DataFrame(Dock_Normal.max())
        df_Capacity["daily_capacity_low"] = Dock_Normal.min()
        df_Capacity = df_Capacity.reset_index()
        df_Capacity = df_Capacity.rename(
            columns={0: "daily_capacity_high", "index": "Nbh_id"}
        )
        df_Capacity["daily_capacity_high"] = pd.to_numeric(
            list(df_Capacity["daily_capacity_high"])
        )
        df_Capacity["daily_capacity_mean"] = list(Dock_Normal.mean())
        df_Capacity["daily_capacity_median"] = list(Dock_Normal.median())
        df_Station_cluster_capacity = self.df_Station_final.merge(
            df_Capacity, left_on="Nbh_id", right_on="Nbh_id"
        )
        self.df_Station_cluster_capacity = df_Station_cluster_capacity
        return df_Station_cluster_capacity

    def Capacity_mean_dataviz(
        self,
        bins=[-1, -0.1, -0.01, 0.01, 0.1, 0.2, 0.5],
        df_Station_cluster_capacity=None,
        show_detail=True,
        figsize=(24, 10),
        palette="coolwarm",
    ):
        """_summary_
        Generate visualization of df_Station_cluster_capacity based on capacity average throughout the day
        
        Args:
            bins (list, optional): _description_. Defaults to [-1, -0.1, -0.01, 0.01, 0.1, 0.2, 0.5].
            df_Station_cluster_capacity (pd.DataFrame, optional): _description_. Defaults to None.
            show_detail (bool, optional): _description_. Defaults to True.
            figsize (tuple, optional): _description_. Defaults to (24, 10).
            palette (str, optional): _description_. Defaults to "coolwarm".
        """
        if df_Station_cluster_capacity is None:
            if self.df_Station_cluster_capacity is None:
                df_Station_cluster_capacity = self.Capacity_Analysis()
            else:
                df_Station_cluster_capacity = self.df_Station_cluster_capacity
        #####
        temp_T = self.Get_Normalized_dock().T

        df_Station_cluster_capacity["daily_capacity_group_mean"] = pd.cut(
            x=df_Station_cluster_capacity["daily_capacity_mean"], bins=bins
        )
        LABs = [
            str(i)
            for i in sorted(
                df_Station_cluster_capacity.daily_capacity_group_mean.unique()
            )
        ]
        df_Station_cluster_capacity["daily_capacity_group_mean_str"] = [
            str(i) for i in df_Station_cluster_capacity.daily_capacity_group_mean
        ]
        Index_capacity = {}

        # Over-view
        plt.figure(figsize=figsize)
        plt.title("Station daily mean capacity")
        sns.scatterplot(
            data=df_Station_cluster_capacity,
            x="lng",
            y="lat",
            hue="daily_capacity_group_mean",
            palette=palette,
        )

        plt.show()

        if show_detail:
            for r in LABs:
                Index_capacity[r] = (
                    df_Station_cluster_capacity.query("daily_capacity_low > -2")
                    .query(f'daily_capacity_group_mean_str == "{r}"')["Nbh_id"]
                    .unique()
                )
            for r in LABs:
                temp_T.loc[Index_capacity[r]].T.plot(figsize=figsize)
                plt.title(f"Capacity mean range:{r}")

    def Capacity_high_dataviz(
        self,
        bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.4, 1],
        df_Station_cluster_capacity=None,
        show_detail=True,
        figsize=(24, 10),
        palette="magma",
    ):
        """_summary_
        Generate visualization of df_Station_cluster_capacity based on capacity highs throughout the day
        
        Args:
            bins (list, optional): _description_. Defaults to [-1, -0.1, -0.01, 0.01, 0.1, 0.2, 0.5].
            df_Station_cluster_capacity (pd.DataFrame, optional): _description_. Defaults to None.
            show_detail (bool, optional): _description_. Defaults to True.
            figsize (tuple, optional): _description_. Defaults to (24, 10).
            palette (str, optional): _description_. Defaults to "coolwarm".
        """
        if df_Station_cluster_capacity is None:
            if self.df_Station_cluster_capacity is None:
                df_Station_cluster_capacity = self.Capacity_Analysis()
            else:
                df_Station_cluster_capacity = self.df_Station_cluster_capacity
        #####
        temp_T = self.Get_Normalized_dock().T
        ##############
        df_Station_cluster_capacity["daily_capacity_group_high"] = pd.cut(
            x=df_Station_cluster_capacity["daily_capacity_high"],
            bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.4, 1],
        )
        Index_capacity = {}
        LABs = [
            str(i)
            for i in sorted(
                df_Station_cluster_capacity.daily_capacity_group_high.unique()
            )
        ]
        df_Station_cluster_capacity["daily_capacity_group_high_str"] = [
            str(i) for i in df_Station_cluster_capacity.daily_capacity_group_high
        ]

        #############
        plt.figure(figsize=(16, 9))
        plt.title("Station daily high capacity")
        sns.scatterplot(
            data=df_Station_cluster_capacity,
            x="lng",
            y="lat",
            hue="daily_capacity_group_high",
            palette=palette,
        )

        plt.show()

        if show_detail:
            for r in LABs:
                Index_capacity[r] = (
                    df_Station_cluster_capacity.query("daily_capacity_low > -1")
                    .query(f'daily_capacity_group_high_str == "{r}"')["Nbh_id"]
                    .unique()
                )
            for r in LABs:
                temp_T.loc[Index_capacity[r]].T.plot(figsize=figsize)
                plt.title(f"Capacity high range:{r}")
