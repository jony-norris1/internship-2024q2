import os
import requests
import pandas as pd
from datetime import datetime, date


class SelicCalc:
    def __init__(self):
        self._PATH = os.path.abspath(os.getcwd())

    def earned(self, df: pd.DataFrame) -> pd.DataFrame:
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

    def is_valid_input(self, start_date: date, end_date: date) -> list:
        if not isinstance(self.capital, (float, int)):
            raise Exception("Capital should be int or float")
        if isinstance(start_date, (datetime, date)) and isinstance(
            end_date, (datetime, date)
        ):
            if start_date >= end_date:
                raise Exception("start_date cannot be greater than end_date")
            if start_date < date(1995, 1, 1):
                raise Exception("start_date must be >= 1995-01-01")
            start_date = datetime.strftime(start_date, "%d/%m/%Y")
            end_date = datetime.strftime(end_date, "%d/%m/%Y")
            return [start_date, end_date]
        else:
            raise Exception("Inputs are in wrong format, should be date object")

    def calc_sum(self, start_date, end_date, df):
        _df = df[(df["data"] >= start_date) & (df["data"] <= end_date)]
        _df["x"] = self.capital
        _df["x"] = _df["x"] * _df["valor"].shift().add(1).cumprod().fillna(1)
        val = _df.iloc[-1]["x"]
        return val

    def max_val_range(self, df, range_of=500):
        length = len(df.index) - range_of
        best_start = None
        best_end = None
        best_value = 0
        for i in range(0, length):
            start = df.iloc[i]["data"]
            end = df.iloc[i + range_of - 1]["data"]
            value = self.calc_sum(start, end, df)
            if value > best_value:
                best_start = start
                best_end = end
                best_value = value

        return best_start.date(), best_end.date(), best_value

    def calc_amount(
        self,
        start_date: date,
        end_date: date,
        capital: float,
        frequency: str,
    ) -> pd.DataFrame:
        self.capital = capital
        start_date, end_date = self.is_valid_input(start_date, end_date)
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

        best_start, best_end, best_value = self.max_val_range(df)
        print(
            f"\nThe best day to invest is {best_start}, with an amount earned of {best_value} after {range_of} days ({best_start} to {best_end})"
        )

        df["compound"] = capital
        df["compound"] = df["compound"] * df["valor"].shift().add(1).cumprod().fillna(1)
        sol_df = self.reshape_df(df, frequency)
        return sol_df

    def run_example(self):
        print(f"Running example")
        df_daily = self.calc_amount(
            start_date=date(2010, 1, 1),
            end_date=date(2021, 3, 1),
            capital=657.43,
            frequency="day",
        )
        df_monthly = self.calc_amount(
            start_date=date(2010, 1, 1),
            end_date=date(2021, 3, 1),
            capital=657.43,
            frequency="month",
        )
        df_yearly = self.calc_amount(
            start_date=date(2010, 1, 1),
            end_date=date(2021, 3, 1),
            capital=657.43,
            frequency="year",
        )
        print(df_daily)
        print(df_monthly)
        print(df_yearly)


if __name__ == "__main__":
    calc = SelicCalc()
    calc.run_example()
