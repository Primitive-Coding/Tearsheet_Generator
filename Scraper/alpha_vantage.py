import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ALPHA_VANTAGE_KEY")


class AlphaVantage:
    def __init__(
        self, ticker: str, freq: str = "A", force_update: bool = False
    ) -> None:
        self.ticker = ticker.upper()
        self.freq = "A"
        self.force_update = force_update
        self.url = "https://www.alphavantage.co/query?function={}&symbol={}&apikey={}"

        self.url.format("INCOME_STATEMENT", self.ticker, api_key)

    def get_income_statement(self) -> pd.DataFrame:
        url = self.url.format("INCOME_STATEMENT", self.ticker, api_key)
        response = requests.get(url)
        data = response.json()
        try:
            quarter = pd.DataFrame(data["quarterlyReports"])
            annual = pd.DataFrame(data["annualReports"])
            return annual, quarter
        except KeyError:
            print(f"[API Limit]: {data['Information']}")

    def get_balance_sheet(self) -> pd.DataFrame:
        url = self.url.format("BALANCE_SHEET", self.ticker, api_key)
        response = requests.get(url)
        data = response.json()
        try:
            quarter = pd.DataFrame(data["quarterlyReports"])
            annual = pd.DataFrame(data["annualReports"])
            return annual, quarter
        except KeyError:
            print(f"[API Limit]: {data['Information']}")

    def get_cash_flow(self) -> pd.DataFrame:
        url = self.url.format("CASH_FLOW", self.ticker, api_key)
        response = requests.get(url)
        data = response.json()
        try:
            quarter = pd.DataFrame(data["quarterlyReports"])
            annual = pd.DataFrame(data["annualReports"])
            return annual, quarter
        except KeyError:
            print(f"[API Limit]: {data['Information']}")
