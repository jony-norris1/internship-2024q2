import os
import requests
import glob

import pandas as pd

from datetime import datetime, timedelta, date


class SelicCalc:
    def __init__(self):
        self._PATH = os.path.abspath(os.getcwd())
        self.run_example()

    def earned(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Amount earned"] = None
        df["Amount earned"] = df["compound"] - self.capital
        return df

    def reshape_df(self, df: pd.DataFrame, frequency: str) -> pd.DataFrame:
        df.set_index("data", inplace=True)

        if frequency == "month":
            df = df.groupby([df.index.year, df.index.month]).tail(1)
        elif frequency == "year":
            df = df.groupby([df.index.year]).tail(1)

        df = df.sort_index()
        df = self.earned(df)
        df.drop(["valor"], axis="columns", inplace=True)
        df.rename(columns={"compound": "Capital"}, inplace=True)
        df.index.names = ["Date"]

        return df

    def is_valid_input(self, start_date: date, end_date: date, frequency: str) -> list:
        if not isinstance(self.capital, (float, int)):
            raise Exception("capital should be int or float")
        if isinstance(start_date, (datetime, date)) and isinstance(
            start_date, (datetime, date)
        ):
            if start_date >= end_date:
                raise Exception("start_date cannot be greater than end_date")
            start_date = datetime.strftime(start_date, "%d/%m/%Y")
            end_date = datetime.strftime(end_date, "%d/%m/%Y")
            return [start_date, end_date]
        else:
            raise Exception("Inputs are in wrong format, should be date object")

    def save_csv(self, df, file_name):
        files_present = glob.glob(file_name)
        if not files_present:
            df.to_csv(file_name)
            print(f"Path to csv output: {self._PATH}/{file_name}")
        else:
            print("File already exists, ignoring")

    def calc_sum(self, start_date, end_date, df):
        _df = df[(df["data"] >= start_date) & (df["data"] <= end_date)]
        _df.loc[:, "x"] = self.capital
        _df.loc[:, "x"] = _df["x"] * _df["valor"].shift().add(1).cumprod().fillna(1)
        val = _df.iloc[-1]["x"]
        return val

    def max_val_range(self, df, range_of=500):
        length = len(df.index) - range_of
        best_start = None
        best_end = None
        best_value = 0
        for i in range(0, length):
            start = df.iloc[i]["data"]
            end = df.iloc[i+499]["data"]
            value = self.calc_sum_range(start, end, df)
            if value > best_value:
                best_start = start
                best_end = end
                best_value = value

        print(
            f"\nThe best day to invest is {best_start.date()}, with an amount earned of {best_value} after {range_of} "
            f"days ({best_start.date()} to {best_end.date()})"
        )


    def calc_amount(
        self,
        start_date: date,
        end_date: date,
        capital: float,
        frequency: str,
        save_csv: bool,
    ) -> pd.DataFrame:
        self.capital = capital
        start_date, end_date = self.is_valid_input(start_date, end_date, frequency)
        base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&"
        date_range_str = f"dataInicial={start_date}&dataFinal={end_date}"
        url = base_url + date_range_str
        resp = requests.get(url)
        df = pd.read_json(resp.text)
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["valor"] = pd.to_numeric(df["valor"])
        df.sort_values(by=["data"])
        if df.iloc[0]["data"] < pd.to_datetime(start_date):
            df.drop(index=df.index[0], axis=0, inplace=True)
        df["valor"] = df["valor"] / 100

        self.max_val_range(df)
        df_raw = df.copy()
        df["compound"] = capital
        df["compound"] = (df["compound"]) * df["valor"].shift().add(1).cumprod().fillna(
            1
        )
        sol_df = self.reshape_df(df, frequency)
        if save_csv:
            self.save_csv(sol_df, file_name="solution.csv")
            self.save_csv(df_raw, file_name="df_raw.csv")
        return sol_df

    def run_example(self):
        print(f"Running example")
        df = self.calc_amount(
            start_date=date(2010, 1, 11),
            end_date=date(2021, 3, 1),
            capital=657.43,
            frequency="daily",
            save_csv=False,
        )
        info = (
            "\nArgs:\n"
            "start_date=date(2010, 1, 1),\n"
            "end_date=date(2021, 3, 1),\n"
            "capital=657.43,\n"
            "frequency='day',\n"
            "save_csv=False\n"
        )
        print(info, df)

        # TODO: Add call for monthy and yearly


    def compound_interest(self, df) -> pd.DataFrame:
        df["compound"] = self.capital
        df["compound"] = (df["compound"]) * df["valor"].shift().add(1).cumprod().fillna(
            1
        )
        return df


